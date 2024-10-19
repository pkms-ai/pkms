import json
import logging
from typing import Optional, Dict, Any
import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue, AbstractIncomingMessage
import asyncio
from .config import settings
from .processors import process_content, ContentProcessingError

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self) -> None:
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.queue: Optional[AbstractQueue] = None

    async def connect(self) -> None:
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

    async def setup_queue(self) -> None:
        if self.channel is None:
            raise RuntimeError("Channel is not initialized")
        self.queue = await self.channel.declare_queue(
            "classified_queue", 
            durable=True
        )
        logger.info("Declared queue: classified_queue")

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        try:
            body = message.body.decode()
            content: Dict[str, Any] = json.loads(body)
            logger.info(f"Received message: {content}")
            result = await asyncio.wait_for(
                process_content(content), timeout=300
            )  # 5 minutes timeout
            logger.info(f"Processed result: {result}")
            await message.ack()
        except asyncio.TimeoutError:
            logger.error("Processing timed out")
            await message.reject(requeue=True)
        except ContentProcessingError as e:
            logger.error(f"Content processing error: {e}")
            await message.reject(
                requeue=False
            )  # Don't requeue if it's a content processing error
        except Exception as e:
            logger.error(f"Unexpected error processing message: {e}")
            await message.reject(requeue=True)

    async def start_consuming(self) -> None:
        if self.queue is None:
            raise RuntimeError("Queue is not initialized")
        await self.queue.consume(self.process_message)
        logger.info("Started consuming from classified_queue")

    async def run(self) -> None:
        while True:
            try:
                await self.connect()
                await self.setup_queue()
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
    consumer = RabbitMQConsumer()
    await consumer.run()
