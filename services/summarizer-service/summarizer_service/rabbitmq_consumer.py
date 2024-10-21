# RabbitMQ Consumer for Content Processing Service
#
# This module implements a RabbitMQ consumer for the Content Processing Service.
# It connects to a RabbitMQ server, listens for messages on the content processing queue,
# and processes incoming content using the `process_content` function from the
# `processors` module.

import asyncio
import json
import logging
from typing import Any, Dict, Optional

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)

from .config import settings
from .processors import (
    process_content,
)

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    The main class that handles the RabbitMQ connection, channel setup, and message consumption.
    """

    def __init__(self) -> None:
        """
        Initializes the consumer with empty connection, channel, and queue attributes.
        """
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.input_queue: Optional[AbstractQueue] = None
        self.main_exchange: Optional[AbstractExchange] = None
        self.summary_queue: Optional[AbstractQueue] = None
        self.error_queue: Optional[AbstractQueue] = None

    async def connect(self) -> None:
        """
        Establishes a robust connection to the RabbitMQ server and sets up a channel
        with a prefetch count of 1.
        """
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                heartbeat=60,  # Set heartbeat interval to 60 seconds
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(
                prefetch_count=1
            )  # Explicitly set prefetch count
            logger.info("Connected to RabbitMQ")

    async def setup_queues(self) -> None:
        """
        Declares and sets up all necessary queues for the content processing service.

        The setup process includes:
        1. Declaring a direct message exchange for handling message routing.
        2. Declaring and binding the following queues to the message exchange:
           - Main content processing queue (input_queue)
           - Crawl queue (input_queue)
           - Transcribe queue (TRANSCRIBE_QUEUE)
           - Error queue (ERROR_QUEUE)
        3. Setting up the main content processing queue for consumption.

        Message flow:
        - New messages -> Content Processing Queue
        - Processed messages -> Crawl Queue or Transcribe Queue (based on content type)
        - Failed messages (after max retries) -> Error Queue

        All queues are declared as durable to ensure message persistence across RabbitMQ restarts.
        Each queue is bound to the message exchange using its own name as the routing key.
        """
        if self.channel is None:
            raise RuntimeError("Channel is not initialized")

        # Declare the message exchange
        self.main_exchange = await self.channel.declare_exchange(
            settings.MAIN_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True
        )

        # Declare all necessary queues
        queues_to_declare = [
            settings.INPUT_QUEUE,
            settings.EMBEDDING_QUEUE,
            settings.ERROR_QUEUE,
        ]

        for queue_name in queues_to_declare:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            # Bind the queue to the message exchange with the appropriate routing key
            await queue.bind(self.main_exchange, routing_key=queue_name)
            logger.info(f"Declared and bound queue: {queue_name}")

        # Set the content processing queue
        self.input_queue = await self.channel.get_queue(settings.INPUT_QUEUE)

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        try:
            body = message.body.decode()
            content: Dict[str, Any] = json.loads(body)

            logger.info(f"Received message: {content.get('url')}")
            queue_name, processed_content = await asyncio.wait_for(
                process_content(content), timeout=settings.CONTENT_PROCESSING_TIMEOUT
            )
            logger.info(f"Processed content. Forwarding to queue: {queue_name}")

            # Publish the processed content to the appropriate queue
            await self.publish_message(queue_name, json.dumps(processed_content))

            await message.ack()
        except (asyncio.TimeoutError, Exception) as e:
            logger.error(f"Error processing message: {str(e)}")
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

        if retry_count < settings.MAX_RETRIES:
            # Requeue the message
            await self.main_exchange.publish(
                new_message,
                routing_key=settings.INPUT_QUEUE,
            )
            logger.info(
                f"Requeued message: {content.get('url')}, with retry count: {retry_count}"
            )
        else:
            # Move to error queue
            new_message.headers["x-error-reason"] = "exceeded_max_retries"
            await self.main_exchange.publish(
                new_message,
                routing_key=settings.ERROR_QUEUE,
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
            raise RuntimeError(f"{settings.INPUT_QUEUE} is not initialized")
        await self.input_queue.consume(self.process_message)
        logger.info(f"Started consuming from {settings.INPUT_QUEUE}")

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


async def start_rabbitmq_consumer() -> None:
    """
    Creates a RabbitMQConsumer instance and starts running it.
    """
    consumer = RabbitMQConsumer()
    await consumer.run()
