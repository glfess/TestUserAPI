from fastapi import HTTPException
from fastapi.responses import Response

from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repo import UserRepo
from app.core import exceptions as e
from app.core.security import hash_password

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

async def user_list(skip: int,
                    limit: int,
                    only_deleted: bool,
                    only_active: bool,
                    db: AsyncSession
                    ):
    repo = UserRepo(db)
    users = await repo.get_list(skip, limit, only_deleted, only_active)
    return users

async def get_user(user_id: int,
                   only_deleted: bool,
                   only_active: bool,
                   db: AsyncSession
                   ):
    repo = UserRepo(db)
    user = await repo.get_user_by_id(user_id, only_deleted, only_active)

    if not user:
        raise e.EntityNotFoundError()

    return user

async def create_user(data: UserCreate,
                      db: AsyncSession
                      ):
    repo = UserRepo(db)
    existing_user = await repo.check_existing_user(data)


    if existing_user:
        raise e.AlreadyExistsError(field="email/username")

    user_data = data.model_dump(exclude_unset=True)
    user_data["password"] = hash_password(data.password)

    try:
        new_user = await repo.create_user(data)
        await db.commit()
        return new_user
    except IntegrityError:
        await db.rollback()
        raise e.AlreadyExistsError(field="email/username")

async def update_user(user_data: UserUpdate,
                      user_id: int,
                      db: AsyncSession
                      ):
    repo = UserRepo(db)
    user = await repo.get_user_by_id(user_id)

    if not user:
        raise e.EntityNotFoundError()

    updated_user = user_data.model_dump(exclude_unset=True)

    if updated_user.get("is_deleted") is True:
        updated_user["is_active"] = False
    if updated_user.get("is_active") is True:
        updated_user["is_deleted"] = False

    if updated_user.get("is_active") and updated_user.get("is_deleted"):
        raise e.InconsistentStateError(field_name="is_active/is_deleted")

    conflicting_users = await repo.get_conflicting_users(user_id,
                                                         email=updated_user.get("email"),
                                                         username=updated_user.get("username")
                                                         )

    if conflicting_users:
        field_name = "email" if updated_user.get("email") == conflicting_users.email else "username"
        raise e.AlreadyExistsError(field=field_name)

    try:
        new_user = await repo.update_user(user, updated_user)
        await db.commit()
        return new_user
    except IntegrityError:
        await db.rollback()
        raise e.InconsistentStateError(field_name="email/username")

async def delete_user(user_id: int,
                      db: AsyncSession
                      ):
    repo = UserRepo(db)
    user = await repo.get_user_by_id(user_id)

    if not user:
        raise e.EntityNotFoundError()


    await repo.delete_user(user)
    await db.commit()
    return Response(status_code=204)
