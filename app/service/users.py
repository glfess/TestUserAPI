from fastapi import HTTPException
from fastapi.responses import Response

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repo import UserRepo

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
    user = await repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user

async def create_user(data: UserCreate,
                      db: AsyncSession
                      ):
    repo = UserRepo(db)
    existing_user = await repo.check_existing_user(data)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким E-Mail или именем пользователя уже зарегистрирован"
        )

    new_user = await repo.create_user(data)
    return new_user

async def update_user(user_data: UserUpdate,
                      user_id: int,
                      db: AsyncSession
                      ):
    repo = UserRepo(db)
    user = await repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    updated_user = user_data.model_dump(exclude_unset=True)

    if updated_user.get("is_deleted") is True:
        updated_user["is_active"] = False
    if updated_user.get("is_active") is True:
        updated_user["is_deleted"] = False

    if updated_user.get("is_active") and updated_user.get("is_deleted"):
        raise HTTPException(status_code=400,
                            detail="Пользователь не может быть удаленным и активынм одновременно")

    conflicting_users = await repo.get_conflicting_users(user_id,
                                                         email=updated_user.get("email"),
                                                         username=updated_user.get("username")
                                                         )

    if conflicting_users:
        if updated_user.get("email") == conflicting_users.email:
            detail = "Этот E-Mail уже занят другим пользователем"
            raise HTTPException(status_code=400, detail=detail)
        detail = "Этот username уже занят другим пользователем"
        raise HTTPException(status_code=400, detail=detail)

    return await repo.update_user(user, updated_user)

async def delete_user(user_id: int,
                      db: AsyncSession
                      ):
    repo = UserRepo(db)
    user = await repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await repo.delete_user(user)
    return Response(status_code=204)
