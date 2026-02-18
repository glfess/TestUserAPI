import redis.asyncio as redis
from contextlib import asynccontextmanager
from app.api.users.router import router
from app.api.monitoring import router as monitoring_router
from app.api.handlers import app_error_handler
from app.core.exceptions import AppErrors
from app.core.config import settings

from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = redis.ConnectionPool.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                                         encoding="utf-8", decode_responses=True)

    app.state.redis_client = await redis.Redis(connection_pool=pool)

    yield

    await app.state.redis_client.aclose()
    await pool.disconnect()

app = FastAPI(title="Test FastAPI",
              description="Test FastAPI",
              version="0.1.0",
              lifespan=lifespan,
              )

app.include_router(router, prefix="/api/users", tags=["users"])

app.include_router(monitoring_router)

app.add_exception_handler(AppErrors, app_error_handler)

@app.get("/")
async def root():
    return {"Session": "Online"}
