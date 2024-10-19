import json
import logging
import aio_pika
import asyncio
from typing import Dict
from .config import settings
from .processors import process_content
from common_lib.models import ContentType

logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queues: Dict[ContentType, aio_pika.Queue] = {}

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            logger.info("Connected to RabbitMQ")

    async def setup_queues(self):
        for content_type, queue_name in settings.RABBITMQ_QUEUES.items():
            queue = await self.channel.declare_queue(queue_name, durable=True)
            self.queues[content_type] = queue
            logger.info(f"Declared queue: {queue_name}")

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                body = message.body.decode()
                content = json.loads(body)
                logger.info(f"Received message: {content}")
                result = process_content(content)
                logger.info(f"Processed result: {result}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def start_consuming(self):
        for queue in self.queues.values():
            await queue.consume(self.process_message)
        logger.info("Started consuming from all queues")

    async def run(self):
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

async def start_rabbitmq_consumer():
    consumer = RabbitMQConsumer()
    await consumer.run()
