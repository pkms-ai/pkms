import asyncio
import asyncpg
from db_service.db import DatabaseConfig, initialize_database, get_db_pool
from db_service.populate_db import populate_database
import logging

logger = logging.getLogger(__name__)

async def create_database_if_not_exists(db_config: DatabaseConfig):
    system_conn = None
    try:
        system_conn = await asyncpg.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            password=db_config.password,
            database="postgres"
        )

        # Check if the database exists
        exists = await system_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_config.database
        )

        if not exists:
            # Create the database if it doesn't exist
            await system_conn.execute(f"CREATE DATABASE {db_config.database}")
            logger.info(f"Database '{db_config.database}' created successfully")
        else:
            logger.info(f"Database '{db_config.database}' already exists")

    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise
    finally:
        if system_conn:
            await system_conn.close()

async def initialize_and_populate_database(db_config: DatabaseConfig, populate_data: bool = False):
    pool = await get_db_pool(db_config)
    try:
        await initialize_database(pool)
        logger.info("Database tables and indexes created successfully")

        if populate_data:
            await populate_database(pool)
            logger.info("Database populated with sample data")
    finally:
        await pool.close()

async def main():
    from db_service.config import get_database_config
    db_config = get_database_config()
    await create_database_if_not_exists(db_config)
    await initialize_and_populate_database(db_config, populate_data=True)

if __name__ == "__main__":
    asyncio.run(main())
