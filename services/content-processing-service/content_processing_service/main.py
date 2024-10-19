import asyncio
import logging
import signal
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .rabbitmq_consumer import start_rabbitmq_consumer
from .routes import router

app = FastAPI(title="Content Processing Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


consumer_task = None


@app.on_event("startup")
async def startup_event():
    global consumer_task
    # Start RabbitMQ consumer in the background
    consumer_task = asyncio.create_task(start_rabbitmq_consumer())


@app.on_event("shutdown")
async def shutdown_event():
    global consumer_task
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("RabbitMQ consumer has been cancelled")


def signal_handler(sig, frame):
    logger.info("Received interrupt signal, shutting down...")
    asyncio.get_event_loop().stop()


def start():
    env = settings.ENVIRONMENT
    host = "0.0.0.0"
    port = settings.PORT

    logger.info(f"Starting server in {env} mode")
    logger.info(f"CORS origins: {settings.cors_origins}")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        if env == "development":
            uvicorn.run(
                "content_processing_service.main:app", host=host, port=port, reload=True
            )
        else:
            uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Error starting the server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start()
