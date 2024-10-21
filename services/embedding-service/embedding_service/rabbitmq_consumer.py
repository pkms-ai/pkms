# RabbitMQ Consumer for Content Processing Service
#
# This module implements a RabbitMQ consumer for the Content Processing Service.
# It connects to a RabbitMQ server, listens for messages on the content processing queue,
# and processes incoming content using the `process_content` function from the
# `processors` module.

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Coroutine, Dict, List, Optional, Tuple

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    The main class that handles the RabbitMQ connection, channel setup, and message consumption.
    """

    def __init__(
        self,
        rabbitmq_url: str,
        input_queue: str,
        exchange_queue: str,
        error_queue: str,
        output_queues: List[str],
        process_func: Callable[[Dict[str, Any]], Awaitable[Tuple[str, Any]]],
        process_error_handler: Optional[
            Callable[
                [Exception, Optional[Dict[str, Any]], AbstractIncomingMessage],
                Coroutine[Any, Any, None],
            ]
        ] = None,
        processing_timeout: int = 300,
        max_retries: int = 3,
    ) -> None:
        self.rabbitmq_url = rabbitmq_url
        self.input_queue_name = input_queue
        self.exchange_queue_name = exchange_queue
        self.error_queue_name = error_queue
        self.output_queues = output_queues
        self.process_func = process_func
        self.process_error_handler = process_error_handler
        self.processing_timeout = processing_timeout
        self.max_retries = max_retries
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.input_queue: Optional[AbstractQueue] = None
        self.main_exchange: Optional[AbstractExchange] = None
        self.error_queue: Optional[AbstractQueue] = None

    async def connect(self) -> None:
        """
        Establishes a robust connection to the RabbitMQ server and sets up a channel
        with a prefetch count of 1.
        """
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(
                self.rabbitmq_url,
                heartbeat=60,  # Set heartbeat interval to 60 seconds
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(
                prefetch_count=1
            )  # Explicitly set prefetch count
            logger.info("Connected to RabbitMQ")

    async def setup_queues(self) -> None:
        if self.channel is None:
            raise RuntimeError("Channel is not initialized")

        # Declare the message exchange
        self.main_exchange = await self.channel.declare_exchange(
            self.exchange_queue_name, aio_pika.ExchangeType.DIRECT, durable=True
        )

        # Declare all necessary queues
        queues_to_declare = [
            self.input_queue_name,
            self.error_queue_name,
        ] + self.output_queues

        for queue_name in queues_to_declare:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            # Bind the queue to the message exchange with the appropriate routing key
            await queue.bind(self.main_exchange, routing_key=queue_name)
            logger.info(f"Declared and bound queue: {queue_name}")

        # Set the content processing queue
        self.input_queue = await self.channel.get_queue(self.input_queue_name)

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        content: Dict[str, Any] = dict()
        try:
            body = message.body.decode()
            content: Dict[str, Any] = json.loads(body)

            logger.info(f"Received message: {content.get('url')}")
            queue_name, processed_content = await asyncio.wait_for(
                self.process_func(content), timeout=self.processing_timeout
            )

            if queue_name == "":
                # in case queue name is not in output queues, we assume the worklow is completed
                logger.info(
                    "Processed content. Workflow completed. No further processing required."
                )
            else:
                logger.info(f"Processed content. Forwarding to queue: {queue_name}")
                if queue_name not in self.output_queues:
                    raise ValueError(f"Queue {queue_name} is not in output queues")
                # Publish the processed content to the appropriate next queue
                await self.publish_message(queue_name, json.dumps(processed_content))

            await message.ack()
        except (asyncio.TimeoutError, Exception) as e:
            # Try the custom handler first if provided
            if self.process_error_handler:
                try:
                    await self.process_error_handler(e, content, message)
                except Exception as custom_handler_error:
                    # If the custom handler fails, fall back to the default
                    logger.error(f"Unhandled error: {str(custom_handler_error)}")
                    await self.handle_failed_message(message)
            else:
                # Default fallback handling for any unhandled exceptions
                logger.error(f"Unhandled error: {str(e)}")
                await self.handle_failed_message(message)

    async def handle_failed_message(self, message: AbstractIncomingMessage) -> None:
        """
        Handles failed messages by either requeuing them with a delay or moving them to the error queue.

        This method implements a retry mechanism:
        1. If the retry count is less than MAX_RETRIES, it requeues the message with an incremented retry count.
        2. If the retry count has reached MAX_RETRIES, it moves the message to the error queue.

        Args:
            message (AbstractIncomingMessage): The failed message from RabbitMQ.
        """
        # Safely get the retry count, defaulting to 0 if header or x-retry-count doesn't exist or is invalid
        retry_count = 0
        if hasattr(message, "headers"):
            retry_count_value = message.headers.get("x-retry-count")
            if retry_count_value is not None:
                try:
                    if isinstance(retry_count_value, (int, str)):
                        retry_count = int(retry_count_value)
                    else:
                        logger.warning(
                            f"Unexpected type for retry count: {type(retry_count_value)}. Defaulting to 0."
                        )
                except ValueError:
                    logger.warning(
                        f"Invalid retry count in message headers: {retry_count_value}. Defaulting to 0."
                    )
        retry_count += 1

        body = message.body.decode()
        content: Dict[str, Any] = json.loads(body)

        if self.main_exchange is None:
            raise RuntimeError("Message exchange is not initialized")

        # Preserve existing headers if they exist, otherwise start with an empty dict
        existing_headers = message.headers if hasattr(message, "headers") else {}
        new_headers = {**existing_headers, "x-retry-count": retry_count}

        new_message = aio_pika.Message(
            body=message.body,
            headers=new_headers,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        if retry_count < self.max_retries:
            # Requeue the message
            await self.main_exchange.publish(
                new_message,
                routing_key=self.input_queue_name,
            )
            logger.info(
                f"Requeued message: {content.get('url')}, with retry count: {retry_count}"
            )
        else:
            # Move to error queue
            new_message.headers["x-error-reason"] = "exceeded_max_retries"
            await self.main_exchange.publish(
                new_message,
                routing_key=self.error_queue_name,
            )
            logger.warning(
                f"Message exceeded max retries. Moved to error queue: {content.get('url')}"
            )

        await message.ack()

    async def publish_message(self, routing_key: str, message: str) -> None:
        if self.main_exchange is None:
            raise RuntimeError("Message exchange is not initialized")

        await self.main_exchange.publish(
            aio_pika.Message(
                body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=routing_key,
        )
        logger.info(f"Published message to queue: {routing_key}")

    async def start_consuming(self) -> None:
        """
        Starts consuming messages from the content processing queue specified in the configuration.
        """
        if self.input_queue is None:
            raise RuntimeError(f"{self.input_queue_name} is not initialized")
        await self.input_queue.consume(self.process_message)
        logger.info(f"Started consuming from {self.input_queue_name}")

    async def run(self) -> None:
        """
        Main loop that connects to RabbitMQ, sets up the queues, and starts consuming messages.
        Implements error handling and reconnection logic.
        """
        while True:
            try:
                await self.connect()
                await self.setup_queues()
                await self.start_consuming()

                # Keep the consumer running, but allow for interruption
                await asyncio.Future()
            except aio_pika.exceptions.AMQPConnectionError as e:
                logger.warning(f"RabbitMQ connection error: {e}. Reconnecting...")
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info("RabbitMQ consumer is shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(5)
            finally:
                if self.connection and not self.connection.is_closed:
                    await self.connection.close()

    async def stop(self):
        logger.info("Shutting down consumer")
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
