import asyncio
import logging
import signal

from workflow_base import RabbitMQConsumer, WorkflowManager
from .config import settings
from .workflow_config import WorkflowConfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start():
    try:
        # Get the processor type from the configuration or environment variable
        processor_name = settings.PROCESSOR_NAME
        workflow_config = WorkflowConfig()
        workflow_manager = WorkflowManager(workflow_config)
        processor = workflow_manager.create_processor(processor_name)
        # # Initialize RabbitMQ consumer
        consumer = RabbitMQConsumer(
            rabbitmq_url=settings.RABBITMQ_URL,
            input_queue=processor.input_queue,
            error_queue=processor.error_queue,
            output_queues=processor.output_queues,
            process_func=processor.process_content,
            process_error_handler=processor.handle_error,
        )

        # Signal handling for graceful shutdown
        def stop():
            logger.info("Shutting down consumer...")
            asyncio.create_task(consumer.stop())
            loop.call_soon(loop.stop)  # Schedule loop.stop() after stop completes

        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGTERM, stop)
        loop.add_signal_handler(signal.SIGINT, stop)

        # Start the consumer
        await consumer.run()
    except Exception as e:
        logger.error(f"Failed to start consumer: {e}")
        raise


def main():
    asyncio.run(start())


if __name__ == "__main__":
    asyncio.run(start())
