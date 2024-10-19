from fastapi import FastAPI, Depends
from .db import DatabaseConfig, get_db_pool, check_url_exists
from .config import settings
import asyncpg

app = FastAPI()

db_config = DatabaseConfig(
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    database=settings.POSTGRES_DB
)

@app.on_event("startup")
async def startup():
    app.state.db_pool = await get_db_pool(db_config)

@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()

async def get_db_pool():
    return app.state.db_pool

@app.get("/check_url")
async def check_url(url: str, pool: asyncpg.Pool = Depends(get_db_pool)):
    exists = await check_url_exists(pool, url)
    return {"url": url, "exists": exists}
