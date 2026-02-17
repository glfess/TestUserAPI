import redis.asyncio as redis

from fastapi import Depends
from app.core.config import settings
from app.core.redis_service import RedisCacheService

redis_client = redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                              encoding="utf-8",
                              decode_responses=True
                              )

async def get_redis_client():
    yield redis_client

async def get_redis_service(client: redis.Redis = Depends(get_redis_client)) -> RedisCacheService:
    return RedisCacheService(client)
