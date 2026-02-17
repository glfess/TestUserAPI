from fastapi import Request, Depends

from app.core.redis import get_redis_client
from app.core.exceptions import TooManyRequestsError

import redis.asyncio as redis

LUA_LIMITER = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end
return current
"""

class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

    async def __call__(self,
                       request: Request,
                       r: redis.Redis=Depends(get_redis_client)
                       ):
        key = f"rate_limit:{request.client.host}:{request.scope['path']}"

        count = await r.eval(LUA_LIMITER, 1, key, self.seconds)

        if count > self.times:
            raise TooManyRequestsError(message=f"Превышен лимит запросов: {self.times} за {self.seconds} сек.")
