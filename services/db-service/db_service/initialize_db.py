import asyncio
import logging

from .config import settings

from db_service.db import (
    DatabaseConfig,
    initialize_database,
    create_database,
)

logger = logging.getLogger(__name__)


async def main():
    db_config = DatabaseConfig(
        host=settings.POSTGRES_HOST,
        port=settings.PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
    )
    await create_database(db_config)
    await initialize_database(db_config, populate_sample_data=True)


if __name__ == "__main__":
    asyncio.run(main())
