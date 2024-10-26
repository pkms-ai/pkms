import asyncio
import logging

from .config import settings
from .rabbitmq_consumer import RabbitMQConsumer
from .processors import ProcessorFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start():
    # Get the processor type from the configuration or environment variable
    processor_name = settings.PROCESSOR_NAME
    processor = ProcessorFactory.create_processor(processor_name)

    # Initialize RabbitMQ consumer
    consumer = RabbitMQConsumer(
        rabbitmq_url=settings.RABBITMQ_URL,
        input_queue=processor.input_queue,
        exchange_queue=processor.exchange_queue,
        error_queue=processor.error_queue,
        output_queues=processor.output_queues,
        process_func=processor.process_content,
        process_error_handler=processor.handle_error,
    )

    # Start the consumer
    await consumer.run()


def main():
    asyncio.run(start())


if __name__ == "__main__":
    asyncio.run(start())
