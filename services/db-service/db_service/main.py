import argparse
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from .config import settings
from .content_repository import check_url_exists, insert_content, update_content
from .db import DatabaseConfig, get_db_pool
from .model import (
    ContentModel,
    ContentUpdateModel,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_db_pool_with_retry(delay: float = 30.0):
    while True:
        try:
            logger.info("Attempting to connect to the database...")
            pool = await get_db_pool(db_config)
            if pool:
                logger.info("Successfully connected to the database")
                return pool
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")

        logger.info(f"Retrying in {delay} seconds...")
        await asyncio.sleep(delay)


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
    app.state.db_pool = await get_db_pool_with_retry()

    yield
    # Shutdown: Close the database connection pool
    if app.state.db_pool:
        logger.info("Closing database connection pool")
        await app.state.db_pool.close()
    else:
        logger.warning("Database connection pool was not initialized")


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


# insert conent
@app.post("/content")
async def insert(
    content: ContentModel,
    pool=Depends(get_db_pool_dependency),
):
    """
    Endpoint to insert new content into the database.
    """
    logger.info(f"Inserting new content: {content.url}")

    try:
        inserted_content = await insert_content(pool, content)
        return {"status": "success", "data": inserted_content}
    except ValueError as e:
        logger.error(f"Error inserting content: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error inserting content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#  curl -X POST "http://localhost:8000/content" \
# -H "Content-Type: application/json" \
# -d '{
#     "url": "https://example12.com",
#     "content_type": "web_article",
#     "title": "Sample Title",
#     "description": "This is a sample description.",
#     "summary": "This is a brief summary.",
#     "metadata": {
#         "author": "John Doe",
#         "published_date": "2024-10-21"
#     },
#     "content_id": "f47ac10b-58cc-4372-a567-0e02b2c3d478"
# }'


@app.put("/content/{content_id}")
async def update_content_route(
    content_id: UUID,
    content_update: ContentUpdateModel,
    pool=Depends(get_db_pool_dependency),
):
    """
    Endpoint to update existing content in the database.
    """
    logger.info(f"Updating content with ID: {content_id}")
    try:
        updated_content = await update_content(pool, content_id, content_update)
        if updated_content is None:
            raise HTTPException(
                status_code=404, detail=f"Content with ID {content_id} not found"
            )
        return {"status": "success", "data": updated_content}  # Return as JSON

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# curl -X PUT "http://localhost:8000/content/f47ac10b-58cc-4372-a567-0e02b2c3d478" \
# -H "Content-Type: application/json" \
# -d '{
#     "title": "Updated Sample Title",
#     "description": "This is an updated sample description.",
#     "summary": "This is an updated brief summary.",
#     "metadata": {
#         "author": "Jane Doe",
#         "published_date": "2024-10-22"
#     }
# }'


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/health/db")
async def health_check_db(pool=Depends(get_db_pool_dependency)):
    try:
        async with pool.acquire() as conn:
            await conn.fetchval(
                "SELECT 1"
            )  # Perform a simple query to check the connection
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database is unavailable")


def start():
    env = settings.ENVIRONMENT
    host = "0.0.0.0"
    port = settings.PORT

    logger.info(f"Starting server in {env} mode on port {port}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    logger.info(f"Database host: {db_config.host}")

    try:
        if env == "development":
            uvicorn.run("db_service.main:app", host=host, port=port, reload=True)
        else:
            uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Error starting the server: {e}")
    finally:
        logger.info("Shutting down the server")


if __name__ == "__main__":
    start()
