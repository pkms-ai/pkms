import asyncio
import asyncpg
from config import settings
import argparse
import uuid

async def table_exists(conn, table_name):
    result = await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = $1
        )
        """,
        table_name
    )
    return result

async def create_content_table(conn):
    # Create the ContentType enum
    await conn.execute('''
        DO $$ BEGIN
            CREATE TYPE ContentType AS ENUM (
                'web_article', 'youtube_video', 'publication', 'bookmark', 'unknown'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    ''')

    # Create the content table with UUID as id and ContentType enum
    await conn.execute('''
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        
        CREATE TABLE IF NOT EXISTS content (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            content_type ContentType NOT NULL,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_content_url ON content (url);
    ''')
    print("Schema created successfully!")

async def update_schema(conn):
    # Add any schema updates here
    # For example:
    # await conn.execute('''
    #     ALTER TABLE content
    #     ADD COLUMN IF NOT EXISTS new_column TEXT
    # ''')
    print("Schema updated successfully!")

async def populate_content(conn):
    sample_data = [
        (str(uuid.uuid4()), "https://example.com/article1", "Sample Article 1", "web_article"),
        (str(uuid.uuid4()), "https://example.com/article2", "Sample Article 2", "web_article"),
        (str(uuid.uuid4()), "https://youtube.com/watch?v=abc123", "Sample YouTube Video", "youtube_video"),
        (str(uuid.uuid4()), "https://example.com/publication1", "Sample Publication", "publication"),
        (str(uuid.uuid4()), "https://example.com/bookmark1", "Sample Bookmark", "bookmark"),
    ]

    await conn.executemany('''
        INSERT INTO content (id, url, title, content_type)
        VALUES ($1::uuid, $2, $3, $4::ContentType)
        ON CONFLICT (url) DO NOTHING
    ''', sample_data)
    print("Sample data populated successfully!")

async def initialize_database(populate_data=False):
    conn = await asyncpg.connect(settings.database_url)
    try:
        content_table_exists = await table_exists(conn, 'content')
        
        if not content_table_exists:
            await create_content_table(conn)
        else:
            await update_schema(conn)
        
        if populate_data:
            await populate_content(conn)

    finally:
        await conn.close()

def main():
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument("--populate-data", action="store_true", help="Populate the database with sample data")

    args = parser.parse_args()

    asyncio.run(initialize_database(populate_data=args.populate_data))

if __name__ == "__main__":
    main()
