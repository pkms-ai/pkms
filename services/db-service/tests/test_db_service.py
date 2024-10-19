import pytest
import asyncio
import asyncpg
from httpx import AsyncClient
from fastapi.testclient import TestClient
from db_service.main import app, get_db_pool
from db_service.db import DatabaseConfig, ContentType, insert_content, check_url_exists, get_content_by_url, initialize_database
from db_service.config import Settings
from db_service.initialize_db import create_database_if_not_exists, initialize_and_populate_database
from db_service.populate_db import populate_database
from uuid import UUID

test_settings = Settings()
test_settings.POSTGRES_DB = "test_content_db"
test_settings.POSTGRES_HOST = "127.0.0.1"

# Use a test database
test_db_config = DatabaseConfig(
    host=test_settings.POSTGRES_HOST,
    port=test_settings.POSTGRES_PORT,
    user=test_settings.POSTGRES_USER,
    password=test_settings.POSTGRES_PASSWORD,
    database=test_settings.POSTGRES_DB
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
        await create_database_if_not_exists(test_db_config)
        await initialize_and_populate_database(test_db_config, populate_data=True)
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
                database="postgres"
            )
            await conn.execute(f'DROP DATABASE IF EXISTS {test_db_config.database}')
            await conn.close()
            print(f"Test database {test_db_config.database} dropped successfully")
        except Exception as e:
            print(f"Failed to drop test database: {str(e)}")

@pytest.fixture(scope="module")
async def db_pool(initialize_and_cleanup_test_db):
    print("Creating database pool")
    try:
        # Override the app's database configuration with test configuration
        app.state.db_config = test_db_config
        pool = await get_db_pool()
        yield pool
        await pool.close()
    except Exception as e:
        print(f"Failed to create database pool: {str(e)}")
        pytest.fail(f"Database pool creation failed: {str(e)}")

@pytest.fixture(scope="module")
async def client(db_pool):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_check_url_endpoint(client):
    print("Running test_check_url_endpoint")
    response = await client.get("/check_url", params={"url": "https://example.com/article1"})
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "exists" in data
    assert isinstance(data["exists"], bool)
    assert data["exists"] is True  # This URL should exist from populate_database

# @pytest.mark.asyncio
# async def test_insert_and_check_content(db_pool):
#     logger.info("Running test_insert_and_check_content")
#     url = "https://test.example.com"
#     title = "Test Article"
#     content_type = ContentType.WEB_ARTICLE

#     # Insert content
#     content_id = await insert_content(db_pool, url, title, content_type)
#     assert isinstance(content_id, UUID)

#     # Check if URL exists
#     exists = await check_url_exists(db_pool, url)
#     assert exists is True

#     # Get content by URL
#     content = await get_content_by_url(db_pool, url)
#     assert content is not None
#     assert content["url"] == url
#     assert content["title"] == title
#     assert content["content_type"] == content_type.value

# @pytest.mark.asyncio
# async def test_check_nonexistent_url(db_pool):
#     logger.info("Running test_check_nonexistent_url")
#     url = "https://nonexistent.example.com"
#     exists = await check_url_exists(db_pool, url)
#     assert exists is False

# @pytest.mark.asyncio
# async def test_get_content_by_url(db_pool):
#     logger.info("Running test_get_content_by_url")
#     url = "https://example.com/article1"  # This URL should exist from populate_database
#     content = await get_content_by_url(db_pool, url)
#     assert content is not None
#     assert content["url"] == url
#     assert content["title"] == "Sample Article 1"
#     assert content["content_type"] == ContentType.WEB_ARTICLE.value

# Add more tests as needed for other functions and endpoints

