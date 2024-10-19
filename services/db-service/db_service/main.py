from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from .db import DatabaseConfig, get_db_pool, check_url_exists
from .config import settings
import asyncpg

db_config = DatabaseConfig(
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    database=settings.POSTGRES_DB
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db_pool = await get_db_pool(db_config)
    yield
    # Shutdown
    await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)

async def get_db_pool():
    if not hasattr(app.state, "db_pool"):
        app.state.db_pool = await asyncpg.create_pool(
            host=app.state.db_config.host,
            port=app.state.db_config.port,
            user=app.state.db_config.user,
            password=app.state.db_config.password,
            database=app.state.db_config.database,
        )
    return app.state.db_pool

@app.get("/check_url")
async def check_url(url: str, pool: asyncpg.Pool = Depends(get_db_pool)):
    exists = await check_url_exists(pool, url)
    return {"url": url, "exists": exists}
