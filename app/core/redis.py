import redis.asyncio as redis

from fastapi import Depends, Request
from app.core.redis_service import RedisCacheService

async def get_redis_client(request: Request) -> redis.Redis:
    return request.app.state.redis_client

async def get_redis_service(client: redis.Redis = Depends(get_redis_client)) -> RedisCacheService:
    return RedisCacheService(client)
