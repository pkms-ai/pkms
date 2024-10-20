import logging
import sys
import argparse
import os

import uvicorn
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .config import settings
from .content_repository import check_url_exists
from .db import DatabaseConfig, get_db_pool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-host", help="Database host")
    args, _ = parser.parse_known_args()

    db_host = args.db_host or os.environ.get("DB_HOST") or settings.POSTGRES_HOST

    return DatabaseConfig(
        host=db_host,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
    )

# Create DatabaseConfig instance with settings from environment variables
db_config = get_db_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create and store the database connection pool
    logger.info("Creating database connection pool")
    app.state.db_pool = await get_db_pool(db_config)
    if not app.state.db_pool:
        logger.error("Error creating database pool")
        return
    yield
    # Shutdown: Close the database connection pool
    logger.info("Closing database connection pool")
    await app.state.db_pool.close()


# Create FastAPI app with lifespan manager
app = FastAPI(lifespan=lifespan)


async def get_db_pool_dependency():
    """
    Dependency to get the database connection pool.
    """
    return app.state.db_pool


@app.get("/check_url")
async def check_url(url: str, pool=Depends(get_db_pool_dependency)):
    """
    Endpoint to check if a URL exists in the database.
    """
    logger.info(f"Checking URL: {url}")
    exists = await check_url_exists(pool, url)
    return {"url": url, "exists": exists}

# Curl command to check /check_url endpoint:
# curl "http://localhost:8003/check_url?url=https://example.com"


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


def start():
    env = settings.ENVIRONMENT
    host = "0.0.0.0"
    port = settings.PORT

    logger.info(f"Starting server in {env} mode on port {port}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    logger.info(f"Database host: {db_config.host}")

    try:
        if env == "development":
            uvicorn.run(
                "db_service.main:app", host=host, port=port, reload=True
            )
        else:
            uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Error starting the server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start()
