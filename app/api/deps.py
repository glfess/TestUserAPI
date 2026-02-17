from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.redis_service import RedisCacheService
from app.core.redis import redis_client
from app.service.users import UserService
from app.core.security.tokens import decode_token
from app.core import exceptions as e
from app.repositories.user_repo import UserRepo


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

redis_service = RedisCacheService(redis_client)

def get_user_service():
    return UserService(session_factory=async_session_maker, cache_service=redis_service)

async def get_current_user(token: str = Depends(oauth2_scheme),
                           service: UserService = Depends(get_user_service)
                           ):
    return await service.authenticate_user(token)
    if await cache.is_blacklisted(token):
        raise e.TokenBlackListedError()

    payload = decode_token(token)
    username = payload.get("sub")

    if not username:
        raise e.WrongDataError("Некорректный токен")

    repo = UserRepo(db)
    user = await repo.get_user_by_username(username)

    if not user or user.is_deleted:
        raise e.EntityNotFoundError()

    return user
