import asyncio
from uuid import UUID

import asyncpg
import pytest

from db_service.config import Settings
from db_service.content_repository import (
    ContentType,
    check_url_exists,
    get_content_by_url,
    insert_content,
    update_content,
    delete_content,
)
from db_service.db import (
    DatabaseConfig,
    create_database,
    get_db_pool,
    initialize_database,
)

test_settings = Settings()
test_settings.POSTGRES_DB = "test_content_db"
test_settings.POSTGRES_HOST = "localhost"

# Use a test database
test_db_config = DatabaseConfig(
    host=test_settings.POSTGRES_HOST,
    port=test_settings.POSTGRES_PORT,
    user=test_settings.POSTGRES_USER,
    password=test_settings.POSTGRES_PASSWORD,
    database=test_settings.POSTGRES_DB,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def initialize_and_cleanup_test_db():
    print(f"Attempting to initialize test database: {test_db_config.database}")
    try:
        await create_database(test_db_config)
        await initialize_database(test_db_config)  # Remove populate_data=True
        print("Test database initialized successfully")
        yield
    except Exception as e:
        print(f"Failed to initialize test database: {str(e)}")
        pytest.fail(f"Database initialization failed: {str(e)}")
    finally:
        print("")
        print(f"Cleaning up: Dropping test database {test_db_config.database}")
        try:
            conn = await asyncpg.connect(
                host=test_db_config.host,
                port=test_db_config.port,
                user=test_db_config.user,
                password=test_db_config.password,
                database="postgres",
            )
            await conn.execute(f"DROP DATABASE IF EXISTS {test_db_config.database}")
            await conn.close()
            print(f"Test database {test_db_config.database} dropped successfully")
        except Exception as e:
            print(f"Failed to drop test database: {str(e)}")


@pytest.fixture(scope="module")
async def db_pool(initialize_and_cleanup_test_db):
    print("Creating database pool")
    try:
        pool = await get_db_pool(test_db_config)
        if not pool:
            pytest.fail("Database pool creation failed")
        yield pool
        await pool.close()
    except Exception as e:
        print(f"Failed to create database pool: {str(e)}")
        pytest.fail(f"Database pool creation failed: {str(e)}")


@pytest.fixture(autouse=True)
async def clear_content_table(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM content")


@pytest.mark.asyncio
async def test_check_url_exists(db_pool):
    print("Running test_check_url_exists")
    url = "https://example.com/article1"
    title = "Sample Article 1"
    content_type = ContentType.WEB_ARTICLE

    # Insert test data
    await insert_content(db_pool, url, title, content_type)

    exists = await check_url_exists(db_pool, url)
    assert exists is True  # This URL should exist from the fixture


@pytest.mark.asyncio
async def test_insert_and_check_content(db_pool):
    print("Running test_insert_and_check_content")
    url = "https://test.example.com"
    title = "Test Article"
    content_type = ContentType.WEB_ARTICLE

    # Insert content
    inserted_content = await insert_content(db_pool, url, title, content_type)
    assert isinstance(inserted_content, dict)
    assert isinstance(inserted_content['id'], UUID)
    assert inserted_content['url'] == url
    assert inserted_content['title'] == title
    assert inserted_content['content_type'] == content_type.value

    # Check if URL exists
    exists = await check_url_exists(db_pool, url)
    assert exists is True

    # Get content by URL
    content = await get_content_by_url(db_pool, url)
    assert content is not None
    assert content["url"] == url
    assert content["title"] == title
    assert content["content_type"] == content_type.value


@pytest.mark.asyncio
async def test_check_nonexistent_url(db_pool):
    print("Running test_check_nonexistent_url")
    url = "https://nonexistent.example.com"
    exists = await check_url_exists(db_pool, url)
    assert exists is False


@pytest.mark.asyncio
async def test_get_content_by_url(db_pool):
    print("Running test_get_content_by_url")
    url = "https://example.com/article1"
    title = "Sample Article 1"
    content_type = ContentType.WEB_ARTICLE

    # Insert test data
    await insert_content(db_pool, url, title, content_type)

    content = await get_content_by_url(db_pool, url)
    assert content is not None
    assert content["url"] == url
    assert content["title"] == title
    assert content["content_type"] == content_type.value


@pytest.mark.asyncio
async def test_update_content(db_pool):
    print("Running test_update_content")
    url = "https://example.com/article2"
    title = "Sample Article 2"
    content_type = ContentType.WEB_ARTICLE
    summary = "Original summary"

    # Insert test data
    inserted_content = await insert_content(db_pool, url, title, content_type, summary)
    content_id = inserted_content['id']

    # Update content (all fields)
    new_title = "Updated Article 2"
    new_content_type = ContentType.PUBLICATION
    new_summary = "Updated summary"
    updated_content = await update_content(db_pool, content_id, title=new_title, content_type=new_content_type, summary=new_summary)

    assert updated_content is not None
    assert updated_content['id'] == content_id
    assert updated_content['title'] == new_title
    assert updated_content['content_type'] == new_content_type.value
    assert updated_content['summary'] == new_summary

    # Update content (partial update)
    partial_new_title = "Partially Updated Article 2"
    partial_updated_content = await update_content(db_pool, content_id, title=partial_new_title)

    assert partial_updated_content is not None
    assert partial_updated_content['id'] == content_id
    assert partial_updated_content['title'] == partial_new_title
    assert partial_updated_content['content_type'] == new_content_type.value
    assert partial_updated_content['summary'] == new_summary

    # Verify the update
    content = await get_content_by_url(db_pool, url)
    assert content['title'] == partial_new_title
    assert content['content_type'] == new_content_type.value
    assert content['summary'] == new_summary


@pytest.mark.asyncio
async def test_delete_content(db_pool):
    print("Running test_delete_content")
    url = "https://example.com/article3"
    title = "Sample Article 3"
    content_type = ContentType.WEB_ARTICLE

    # Insert test data
    inserted_content = await insert_content(db_pool, url, title, content_type)
    content_id = inserted_content['id']

    # Delete content
    deleted_content = await delete_content(db_pool, content_id)

    assert deleted_content is not None
    assert deleted_content['id'] == content_id
    assert deleted_content['url'] == url
    assert deleted_content['title'] == title
    assert deleted_content['content_type'] == content_type.value

    # Verify the deletion
    content = await get_content_by_url(db_pool, url)
    assert content is None

    exists = await check_url_exists(db_pool, url)
    assert exists is False

# Add more tests as needed for other functions
