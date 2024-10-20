import logging
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

import asyncpg

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    YOUTUBE_VIDEO = "youtube_video"
    PUBLICATION = "publication"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


def normalize_url(url: str) -> str:
    """
    Normalize the URL by removing unnecessary query parameters and fragments.
    """
    parsed = urlparse(url)
    # Remove fragment
    parsed = parsed._replace(fragment='')
    
    # Parse and filter query parameters
    query_params = parse_qs(parsed.query)
    # Add logic here to remove unnecessary parameters
    # For example, remove 'utm_source', 'utm_medium', etc.
    unnecessary_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
    filtered_params = {k: v for k, v in query_params.items() if k not in unnecessary_params}
    
    # Reconstruct the query string
    new_query = urlencode(filtered_params, doseq=True)
    
    # Reconstruct the URL
    normalized = parsed._replace(query=new_query)
    return urlunparse(normalized)


async def check_url_exists(pool: asyncpg.Pool, url: str) -> bool:
    """
    Check if a URL already exists in the database.
    """
    normalized_url = normalize_url(url)
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM content WHERE url = $1)", normalized_url
        )
    logger.debug(
        f"URL existence check for {normalized_url}: {'exists' if result else 'does not exist'}"
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
    summary: Optional[str] = None,
    content_id: Optional[UUID] = None,
) -> dict:
    """
    Insert new content into the database and return the full record.
    """
    # Input validation
    if not url or not urlparse(url).scheme:
        raise ValueError("Invalid URL")
    if not title:
        raise ValueError("Title cannot be empty")

    # Normalize the URL
    normalized_url = normalize_url(url)

    # Check if URL already exists
    exists = await check_url_exists(pool, normalized_url)
    if exists:
        raise ValueError(f"Content with URL {normalized_url} already exists")

    async with pool.acquire() as conn:
        if content_id is None:
            content_id = uuid4()

        query = """
        INSERT INTO content (id, url, title, content_type, summary)
        VALUES ($1, $2, $3, $4::content_type, $5)
        RETURNING *
        """

        try:
            record = await conn.fetchrow(
                query, content_id, normalized_url, title, content_type.value, summary
            )
            logger.info(f"Inserted new content with ID {record['id']}")
            return dict(record)
        except asyncpg.UniqueViolationError:
            logger.error(f"Attempted to insert duplicate content with URL {normalized_url}")
            raise ValueError(f"Content with URL {normalized_url} already exists")
        except Exception as e:
            logger.error(f"Error inserting content: {str(e)}")
            raise


async def update_content(
    pool: asyncpg.Pool,
    content_id: UUID,
    title: Optional[str] = None,
    content_type: Optional[ContentType] = None,
    summary: Optional[str] = None,
) -> Optional[dict]:
    """
    Update existing content in the database and return the full updated record.
    """
    async with pool.acquire() as conn:
        update_fields = []
        update_values = []
        param_count = 1

        if title is not None:
            update_fields.append(f"title = ${param_count}")
            update_values.append(title)
            param_count += 1
        if content_type is not None:
            update_fields.append(f"content_type = ${param_count}::content_type")
            update_values.append(content_type.value)
            param_count += 1
        if summary is not None:
            update_fields.append(f"summary = ${param_count}")
            update_values.append(summary)
            param_count += 1

        if not update_fields:
            logger.warning(f"No fields to update for content ID {content_id}")
            return None

        query = f"""
        UPDATE content
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ${param_count}
        RETURNING *
        """
        update_values.append(content_id)

        record = await conn.fetchrow(query, *update_values)
        if record:
            logger.info(f"Updated content with ID {content_id}")
            return dict(record)
        else:
            logger.info(f"No content found with ID {content_id} for update")
            return None


async def delete_content(pool: asyncpg.Pool, content_id: UUID) -> Optional[dict]:
    """
    Delete content from the database by its ID and return the deleted record.
    """
    async with pool.acquire() as conn:
        query = "DELETE FROM content WHERE id = $1 RETURNING *"
        record = await conn.fetchrow(query, content_id)
        if record:
            logger.info(f"Deleted content with ID {content_id}")
            return dict(record)
        else:
            logger.info(f"No content found with ID {content_id} for deletion")
            return None
