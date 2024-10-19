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

async def initialize_database(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        # Create the enum type if it doesn't exist
        await conn.execute('''
            DO $$ BEGIN
                CREATE TYPE content_type AS ENUM (
                    'web_article', 'youtube_video', 'publication', 'bookmark', 'unknown'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        ''')

        # Create the content table with an index on the url column
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content_type content_type NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_content_url ON content (url);
        ''')

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
        VALUES ($1, $2, $3, $4::content_type, $5)
        RETURNING id
        """
        
        inserted_id = await conn.fetchval(
            query, content_id, url, title, content_type.value, description
        )
        
        return inserted_id

async def update_content(
    pool: asyncpg.Pool,
    content_id: UUID,
    title: Optional[str] = None,
    content_type: Optional[ContentType] = None,
    description: Optional[str] = None
) -> bool:
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
            return False
        
        query = f"""
        UPDATE content
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = $4
        """
        update_values.append(content_id)
        
        result = await conn.execute(query, *update_values)
        return result == "UPDATE 1"

async def delete_content(pool: asyncpg.Pool, content_id: UUID) -> bool:
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM content WHERE id = $1", content_id)
        return result == "DELETE 1"
