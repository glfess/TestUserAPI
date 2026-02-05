from fastapi import HTTPException
from fastapi.responses import Response

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

async def user_list(skip: int,
                    limit: int,
                    only_deleted: bool,
                    only_active: bool,
                    db: AsyncSession
                    ):
    query = select(User).offset(skip).limit(limit).order_by(User.id)

    if only_deleted:
        query = query.where(User.is_deleted == True)

    if only_active:
        query = query.where(User.is_active == True)

    result = await db.execute(query)
    users_list = result.scalars().all()

    return users_list

async def get_user(user_id: int,
                   only_deleted: bool,
                   only_active: bool,
                   db: AsyncSession
                   ):
    query = select(User).where(User.id == user_id)

    if not only_deleted:
        query = query.where(User.is_deleted == False)

    if not only_active:
        query = query.where(User.is_active == False)

    result = await db.execute(query)
    user = result.scalars().one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user

async def create_user(data: UserCreate,
                      db: AsyncSession
                      ):
    query = select(User).where(or_(User.username == data.username,
                                   User.email == data.email
                                   )
                               )
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким E-Mail или именем пользователя уже зарегистрирован"
        )

    new_user = User(username=data.username, email=data.email)
    db.add(new_user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(new_user)
    return new_user

async def update_user(user_data: UserUpdate,
                      user_id: int,
                      db: AsyncSession
                      ):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    updated_user = user_data.dict(exclude_unset=True)

    if updated_user.get("is_deleted") is True:
        updated_user["is_active"] = False

    if updated_user.get("is_active") is True:
        updated_user["is_deleted"] = False

    if updated_user.get("is_active") and updated_user.get("is_deleted"):
        raise HTTPException(status_code=400,
                            detail="Пользователь не может быть удаленным и активынм одновременно")
    unique_checks = []
    if "email" in updated_user:
        unique_checks.append(User.email == updated_user["email"])
    if "username" in updated_user:
        unique_checks.append(User.username == updated_user["username"])

    if unique_checks:
        check_query = await db.execute(select(User).where(or_(*unique_checks),
                                                          User.id != user_id
                                                          )
                                       )
        conflicting_user = check_query.scalars().first()
        if conflicting_user:
            if "email" in updated_user and conflicting_user.email == updated_user["email"]:
                detail = "Этот E-Mail уже занят другим пользователем"
            else:
                detail = "Этот username уже занят другим пользователем"

            raise HTTPException(status_code=400, detail=detail)

    for key, value in updated_user.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user

async def delete_user(user_id: int,
                      db: AsyncSession
                      ):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await db.delete(user)
    await db.commit()
    return Response(status_code=204)