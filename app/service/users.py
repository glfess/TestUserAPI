from fastapi.security import OAuth2PasswordRequestForm

import json


from app.core import exceptions as e
from app.core.security.passwords import hash_password, verify_password
from app.core.security.tokens import create_access_token, decode_token
from app.schemas.user import UserCreate, UserUpdate, Token, UserSchema
from app.repositories.user_repo import UserRepo
from app.models.user import User

from sqlalchemy.exc import IntegrityError

class UserService:
    def __init__(self, session_factory, cache_service):
        self.session_factory = session_factory
        self.cache_service = cache_service

    async def get_user(self, user_id: int,
                       show_deleted: bool,
                       show_active: bool):
        cached_user = await self.cache_service.get_user(user_id)
        if cached_user:
            return json.loads(cached_user)

        async with self.session_factory() as db:
            repo = UserRepo(db)
            user = await repo.get_user_by_id(user_id, show_deleted, show_active, db)
            if not user:
                raise e.EntityNotFoundError()

            user_data = UserSchema.from_orm(user).model_dump_json(exclude_unset=True)
            await self.cache_service.set_user(user_id, user_data, expire=300)
        return user_data

    async def authenticate_user(self, token: str):
        if await self.cache_service.is_token_blacklisted(token):
            raise e.TokenBlackListedError()

        payload = decode_token(token)

        username = payload.get("sub")
        if not username:
            raise e.WrongDataError("Некорректный токен")

        cache_key = f"user:{username}"

        cached = await self.cache_service.get_user(cache_key)
        if cached:
            user_data = json.loads(cached)
            if not user_data["is_deleted"] and user_data["is_active"]:
                return user_data

        async with self.session_factory() as db:
            repo = UserRepo(db)
            user = await repo.get_user_by_username(username)

            if not user or user.is_deleted or not user.is_active:
                raise e.EntityNotFoundError()

            user_schema = UserSchema.from_orm(user)
            json_data = user_schema.model_dump_json(exclude_unset=True)
            await self.cache_service.set_user(cache_key, json_data, expire=300)

            return user_schema.model_dump()

    async def create_user(self, data: UserCreate):
        async with self.session_factory() as db:
            repo = UserRepo(db)
            existing_user = await repo.check_existing_user(data)

            if existing_user:
                raise e.AlreadyExistsError("Пользователь с таким username или email уже существует")

            user_data = data.model_dump(exclude_unset=True)
            user_data["password"] = hash_password(data.password)

            try:
                new_user = await repo.create_user(user_data)
                return new_user
            except IntegrityError:
                raise e.AlreadyExistsError("Пользователь с таким username или email уже существует")

    async def update_user(self, user_data: UserUpdate,
                          user_id: int
                          ):
        async with self.session_factory() as db:
            repo = UserRepo(db)
            user = await repo.get_user_by_id(user_id)
            if not user:
                raise e.EntityNotFoundError()

            updated_dict = user_data.model_dump(exclude_unset=True)

            new_is_active = updated_dict.get("is_active", user.is_active)
            new_is_deleted = updated_dict.get("is_deleted", user.is_deleted)

            if new_is_active and new_is_deleted:
                raise e.InconsistentStateError()

            conflicting_users = await repo.get_conflicting_users(user_id,
                                                             email=updated_dict.get("email"),
                                                             username=updated_dict.get("username")
                                                             )

            if conflicting_users:
                raise e.AlreadyExistsError(field="email/username")

            try:
                updated_model = await repo.update_user(user, updated_dict)
                await self.cache_service.delete_user(user_id)
                return updated_model
            except IntegrityError:
                raise e.InconsistentStateError()

    async def login(self, username: str, password: str):
        async with self.session_factory() as db:
            repo = UserRepo(db)
            user = await repo.get_user_by_username(username)

            if not user:
                raise e.WrongDataError()
            if not verify_password(password, user.password):
                raise e.WrongDataError()
            if not user.is_active or user.is_deleted:
                raise e.EntityNotFoundError()

            token_data = {"sub": user.username, "id": user.id}
            access_token = create_access_token(data=token_data)

            return Token(access_token=access_token, token_type="bearer")

    async def logout(self, token: str):
        await self.cache_service.blacklist_token(token)
        return {"detail": "Успешный выход"}

    async def user_list(self, skip: int,
                    limit: int,
                    show_deleted: bool,
                    show_active: bool
                    ):
        async with self.session_factory() as db:
            repo = UserRepo(db)
            users = await repo.get_list(skip, limit, show_deleted, show_active)
            return users

    async def delete_user(self, user_id: int
                      ):
        async with self.session_factory() as db:
            repo = UserRepo(db)
            user = await repo.get_user_by_id(user_id)

            if not user:
                raise e.EntityNotFoundError()

            await repo.delete_user(user)
            return None
