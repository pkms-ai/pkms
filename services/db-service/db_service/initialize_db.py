import asyncio
import logging
import argparse

from .config import settings

from .db import (
    DatabaseConfig,
    initialize_database,
    create_database,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def async_main(host: str):
    db_config = DatabaseConfig(
        host=host,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
    )
    logger.info(f"Attempting to create database with config: {db_config}")
    try:
        await create_database(db_config)
        logger.info(f"Successfully created database {db_config.database}")
        await initialize_database(db_config, populate_sample_data=True)
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}", exc_info=True)
        raise


def main():
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument("--host", type=str, default=settings.POSTGRES_HOST,
                        help="Database host (overrides the default from settings)")
    args = parser.parse_args()

    asyncio.run(async_main(args.host))


if __name__ == "__main__":
    main()
