import json
from typing import Optional, Any
import redis.asyncio as redis

class RedisCacheService:
    def __init__(self, client: redis.Redis):
        self.client = client
        self._PREFIX_USER = "user"
        self._PREFIX_BLACKLIST = "blacklist"

    def _get_user_key(self, user_id: int) -> str:
        return f"{self._PREFIX_USER}:{user_id}"

    def _get_blacklist_key(self, token: str) -> str:
        return f"{self._PREFIX_BLACKLIST}:{token}"

    async def get_user(self, user_id: int) -> Optional[dict]:
        key = self._get_user_key(user_id)
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def set_user(self, user_id: int, user_data: dict, expire: int = 3600):
        key = self._get_user_key(user_id)
        await self.client.setex(key, expire, json.dumps(user_data))

    async def delete_user(self, user_id: int):
        await self.client.delete(self._get_user_key(user_id))

    async def blacklist_token(self, token: str, expire: int = 3600):
        key = self._get_blacklist_key(token)
        await self.client.setex(key, expire, "true")

    async def is_token_blacklisted(self, token: str) -> bool:
        key = self._get_blacklist_key(token)
        return await self.client.exists(key) > 0
