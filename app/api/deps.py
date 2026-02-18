from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.redis_service import RedisCacheService
from app.core.redis import get_redis_service
from app.service.users import UserService



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

def get_user_service(cache: RedisCacheService = Depends(get_redis_service)) -> UserService:
    return UserService(session_factory=async_session_maker, cache_service=cache)

async def get_current_user(token: str = Depends(oauth2_scheme),
                           service: UserService = Depends(get_user_service)
                           ):
    return await service.authenticate_user(token)
