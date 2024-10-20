import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .config import settings
from .content_repository import check_url_exists
from .db import DatabaseConfig, get_db_pool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create DatabaseConfig instance with settings from environment variables
db_config = DatabaseConfig(
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    database=settings.POSTGRES_DB,
)


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
