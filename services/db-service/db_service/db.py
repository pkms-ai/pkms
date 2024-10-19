import asyncpg
from pydantic import BaseModel
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional

class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str

class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    YOUTUBE_VIDEO = "youtube_video"
    PUBLICATION = "publication"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"

async def get_db_pool(config: DatabaseConfig):
    return await asyncpg.create_pool(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )

async def check_url_exists(pool: asyncpg.Pool, url: str) -> bool:
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM content WHERE url = $1)", url)
    return result

async def get_content_by_id(pool: asyncpg.Pool, content_id: UUID):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM content WHERE id = $1", content_id)

async def get_content_by_url(pool: asyncpg.Pool, url: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM content WHERE url = $1", url)

async def insert_content(
    pool: asyncpg.Pool,
    url: str,
    title: str,
    content_type: ContentType,
    description: Optional[str] = None,
    content_id: Optional[UUID] = None
) -> UUID:
    async with pool.acquire() as conn:
        if content_id is None:
            content_id = uuid4()
        
        query = """
        INSERT INTO content (id, url, title, content_type, description)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """
        
        inserted_id = await conn.fetchval(
            query, content_id, url, title, content_type.value, description
        )
        
        return inserted_id
