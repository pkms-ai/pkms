import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .rabbitmq_consumer import start_rabbitmq_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    consumer_task = asyncio.create_task(start_rabbitmq_consumer())
    logger.info("RabbitMQ consumer started")
    yield
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


def start():
    env = settings.ENVIRONMENT
    host = "0.0.0.0"
    port = settings.PORT

    logger.info(f"Starting server in {env} mode")
    logger.info(f"CORS origins: {settings.cors_origins}")

    try:
        if env == "development":
            uvicorn.run(
                "summarizer_service.main:app", host=host, port=port, reload=True
            )
        else:
            uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Error starting the server: {e}")
        raise


if __name__ == "__main__":
    start()
