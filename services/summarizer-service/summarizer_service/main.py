import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .rabbitmq_consumer import RabbitMQConsumer
from .processors import process_content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    env = settings.ENVIRONMENT

    logger.info(f"Starting server in {env} mode")
    logger.info(f"CORS origins: {settings.cors_origins}")
    # Startup
    consumer = RabbitMQConsumer(
        rabbitmq_url=settings.RABBITMQ_URL,
        input_queue=settings.INPUT_QUEUE,
        exchange_queue=settings.EXCHANGE_QUEUE,
        error_queue=settings.ERROR_QUEUE,
        output_queues=settings.OUTPUT_QUEUES,
        process_func=process_content,  # Replace with your actual processing function
        process_error_handler=None,  # Or set to None if no custom handler
    )

    # Start the consumer in the background
    consumer_task = asyncio.create_task(consumer.run())
    logger.info("RabbitMQ consumer started")
    yield

    # stop the consumer
    await consumer.stop()
    # Shutdown
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("RabbitMQ consumer has been cancelled")


app = FastAPI(title="Content Processing Service", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
# but as the job will be handle by rabbitmq consumer
# we don't need to include routes for now
# app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
