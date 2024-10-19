import asyncpg
from db_service.db import ContentType
import logging

logger = logging.getLogger(__name__)

async def populate_database(pool: asyncpg.Pool):
    sample_data = [
        {
            "url": "https://example.com/article1",
            "title": "Sample Article 1",
            "content_type": ContentType.WEB_ARTICLE.value
        },
        {
            "url": "https://example.com/article2",
            "title": "Sample Article 2",
            "content_type": ContentType.WEB_ARTICLE.value
        },
        {
            "url": "https://example.com/video1",
            "title": "Sample Video 1",
            "content_type": ContentType.YOUTUBE_VIDEO.value  # Changed from VIDEO to YOUTUBE_VIDEO
        }
    ]

    try:
        async with pool.acquire() as conn:
            # Insert sample data
            for item in sample_data:
                await conn.execute('''
                    INSERT INTO content (url, title, content_type)
                    VALUES ($1, $2, $3::content_type)
                    ON CONFLICT (url) DO NOTHING
                ''', item['url'], item['title'], item['content_type'])
        
        logger.info(f"Inserted {len(sample_data)} sample items into the database")
    except Exception as e:
        logger.error(f"Error populating database: {str(e)}")
        raise
