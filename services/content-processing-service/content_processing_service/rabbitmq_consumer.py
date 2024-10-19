import json
import logging
import aio_pika
import asyncio
from .config import settings
from .processors import process_content

logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                heartbeat=60  # Set heartbeat interval to 60 seconds
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)  # Explicitly set prefetch count
            logger.info("Connected to RabbitMQ")

    async def setup_queue(self):
        self.queue = await self.channel.declare_queue("classified_queue", durable=True)
        logger.info("Declared queue: classified_queue")

    async def process_message(self, message: aio_pika.IncomingMessage):
        try:
            body = message.body.decode()
            content = json.loads(body)
            logger.info(f"Received message: {content}")
            
            result = await asyncio.wait_for(process_content(content), timeout=300)  # 5 minutes timeout
            logger.info(f"Processed result: {result}")
            await message.ack()
        except asyncio.TimeoutError:
            logger.error("Processing timed out")
            await message.reject(requeue=True)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await message.reject(requeue=True)

    async def start_consuming(self):
        await self.queue.consume(self.process_message)
        logger.info("Started consuming from classified_queue")

    async def run(self):
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

async def start_rabbitmq_consumer():
    consumer = RabbitMQConsumer()
    await consumer.run()
