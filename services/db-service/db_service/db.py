import logging

import asyncpg
from pydantic import BaseModel

from db_service.content_repository import ContentType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


async def get_db_pool(config: DatabaseConfig):
    """
    Create and return a connection pool for the database.
    """
    logger.info(
        f"Creating database pool for {config.database} at {config.host}:{config.port}"
    )
    return await asyncpg.create_pool(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )


async def initialize_database(
    db_config: DatabaseConfig, populate_sample_data: bool = False
):
    pool = await get_db_pool(db_config)
    if not pool:
        logger.error("Error creating database pool")
        return
    try:
        await create_tables_and_indexes(pool)
        logger.info("Database tables and indexes created successfully")

        if populate_sample_data:
            await populate_sample_database(pool)
            logger.info("Database populated with sample data")
    finally:
        await pool.close()


async def create_tables_and_indexes(pool: asyncpg.Pool):
    """
    Initialize the database by creating necessary tables and indexes.
    """
    logger.info("Initializing database...")
    async with pool.acquire() as conn:
        # Create the enum type if it doesn't exist
        await conn.execute("""
            DO $$ BEGIN
                CREATE TYPE content_type AS ENUM (
                    'web_article', 'youtube_video', 'publication', 'bookmark', 'unknown'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)

        # Create the content table with an index on the url column
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                url VARCHAR(2048) UNIQUE NOT NULL,
                content_type content_type NOT NULL,
                title TEXT,
                image_url VARCHAR(2048),
                description TEXT,
                summary TEXT,
                metadata JSONB,
                created_at timestamptz DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamptz DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_content_url ON content (url);
        """)
        # CREATE INDEX IF NOT EXISTS idx_content_title_trgm ON content USING gin (title gin_trgm_ops);
    logger.info("Database initialization complete.")


async def populate_sample_database(pool: asyncpg.Pool):
    """
    Populate the database with sample data.
    """
    sample_data = [
        {
            "url": "https://example.com/article1",
            "title": "Sample Article 1",
            "content_type": ContentType.WEB_ARTICLE.value,
        },
        {
            "url": "https://example.com/article2",
            "title": "Sample Article 2",
            "content_type": ContentType.WEB_ARTICLE.value,
        },
        {
            "url": "https://example.com/video1",
            "title": "Sample Video 1",
            "content_type": ContentType.YOUTUBE_VIDEO.value,
        },
    ]

    try:
        async with pool.acquire() as conn:
            # Insert sample data
            for item in sample_data:
                await conn.execute(
                    """
                    INSERT INTO content (url, title, content_type)
                    VALUES ($1, $2, $3::content_type)
                    ON CONFLICT (url) DO NOTHING
                """,
                    item["url"],
                    item["title"],
                    item["content_type"],
                )

        logger.info(f"Inserted {len(sample_data)} sample items into the database")
    except Exception as e:
        logger.error(f"Error populating database: {str(e)}")
        raise


async def create_database(db_config: DatabaseConfig):
    system_conn = None
    try:
        system_conn = await asyncpg.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            password=db_config.password,
            database="postgres",
        )

        # Check if the database exists
        exists = await system_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_config.database
        )

        if not exists:
            # Create the database if it doesn't exist
            await system_conn.execute(f'CREATE DATABASE "{db_config.database}"')
            logger.info(f"Database '{db_config.database}' created successfully")
        else:
            logger.info(f"Database '{db_config.database}' already exists")

    except Exception as e:
        logger.error(f"Error creating database '{db_config.database}': {str(e)}")
        raise
    finally:
        if system_conn:
            await system_conn.close()
