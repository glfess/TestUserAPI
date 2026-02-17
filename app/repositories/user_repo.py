from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate

from fastapi import Depends

from typing import Optional, List

class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self,
                       skip: int = 0,
                       limit: int = 10,
                       show_deleted: bool = False,
                       show_active: bool = True) -> List[User]:
        query = select(User).offset(skip).limit(limit).order_by(User.id)

        if not show_deleted:
            query = query.where(User.is_deleted == False)
        if not show_active:
            query = query.where(User.is_active == False)

        results = await self.db.execute(query)
        return results.scalars().all()

    async def get_user_by_id(self,
                             user_id: int,
                             only_deleted: bool = False,
                             only_active: bool = False):
        query = select(User).where(User.id == user_id)

        if only_deleted:
            query = query.where(User.is_deleted == True)
        elif only_active:
            query = query.where(User.is_active == True)

        results = await self.db.execute(query)
        return results.scalars().one_or_none()

    async def check_existing_user(self, data: UserCreate):
        query = select(User).where(or_(User.username == data.username,
                                       User.email == data.email
                                       )
                                   )
        results = await self.db.execute(query)
        return results.scalars().first()

    async def create_user(self, user_data: dict):
        new_user = User(**user_data)
        self.db.add(new_user)
        try:
            await self.db.flush()
            await self.db.refresh(new_user)
        except IntegrityError:
            raise
        return new_user

    async def get_conflicting_users(self,
                                    user_id: int,
                                    email: str = None,
                                    username: str = None):
        filters = []
        if email:
            filters.append(User.email == email)
        if username:
            filters.append(User.username == username)

        if not filters:
            return None
        query = select(User).where(or_(*filters), User.id != user_id)
        results = await self.db.execute(query)
        return results.scalars().one_or_none()

    async def update_user(self, user_model: User, update_user: dict) -> User:
        for key, value in update_user.items():
            setattr(user_model, key, value)

        await self.db.flush()
        return user_model

    async def delete_user(self, user) -> None:
        await self.db.delete(user)
        await self.db.flush()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalars().one_or_none()
