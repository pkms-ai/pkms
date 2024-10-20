import logging
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import asyncpg

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    YOUTUBE_VIDEO = "youtube_video"
    PUBLICATION = "publication"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


async def check_url_exists(pool: asyncpg.Pool, url: str) -> bool:
    """
    Check if a URL already exists in the database.
    """
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM content WHERE url = $1)", url
        )
    logger.debug(
        f"URL existence check for {url}: {'exists' if result else 'does not exist'}"
    )
    return result


async def get_content_by_id(pool: asyncpg.Pool, content_id: UUID):
    """
    Retrieve content from the database by its ID.
    """
    async with pool.acquire() as conn:
        result = await conn.fetchrow("SELECT * FROM content WHERE id = $1", content_id)
    logger.debug(
        f"Retrieved content for ID {content_id}: {'found' if result else 'not found'}"
    )
    return result


async def get_content_by_url(pool: asyncpg.Pool, url: str):
    """
    Retrieve content from the database by its URL.
    """
    async with pool.acquire() as conn:
        result = await conn.fetchrow("SELECT * FROM content WHERE url = $1", url)
    logger.debug(
        f"Retrieved content for URL {url}: {'found' if result else 'not found'}"
    )
    return result


async def insert_content(
    pool: asyncpg.Pool,
    url: str,
    title: str,
    content_type: ContentType,
    description: Optional[str] = None,
    content_id: Optional[UUID] = None,
) -> UUID:
    """
    Insert new content into the database.
    """
    async with pool.acquire() as conn:
        if content_id is None:
            content_id = uuid4()

        query = """
        INSERT INTO content (id, url, title, content_type, description)
        VALUES ($1, $2, $3, $4::content_type, $5)
        RETURNING id
        """

        inserted_id = await conn.fetchval(
            query, content_id, url, title, content_type.value, description
        )

        logger.info(f"Inserted new content with ID {inserted_id}")
        return inserted_id


async def update_content(
    pool: asyncpg.Pool,
    content_id: UUID,
    title: Optional[str] = None,
    content_type: Optional[ContentType] = None,
    description: Optional[str] = None,
) -> bool:
    """
    Update existing content in the database.
    """
    async with pool.acquire() as conn:
        update_fields = []
        update_values = []
        if title is not None:
            update_fields.append("title = $1")
            update_values.append(title)
        if content_type is not None:
            update_fields.append("content_type = $2::content_type")
            update_values.append(content_type.value)
        if description is not None:
            update_fields.append("description = $3")
            update_values.append(description)

        if not update_fields:
            logger.warning(f"No fields to update for content ID {content_id}")
            return False

        query = f"""
        UPDATE content
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = $4
        """
        update_values.append(content_id)

        result = await conn.execute(query, *update_values)
        success = result == "UPDATE 1"
        logger.info(
            f"Updated content with ID {content_id}: {'success' if success else 'failed'}"
        )
        return success


async def delete_content(pool: asyncpg.Pool, content_id: UUID) -> bool:
    """
    Delete content from the database by its ID.
    """
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM content WHERE id = $1", content_id)
        success = result == "DELETE 1"
        logger.info(
            f"Deleted content with ID {content_id}: {'success' if success else 'failed'}"
        )
        return success
