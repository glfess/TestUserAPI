from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate

from fastapi import Depends

class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self,
                       skip: int = 0,
                       limit: int = 10,
                       only_deleted: bool = False,
                       only_active: bool = True):
        query = select(User).offset(skip).limit(limit).order_by(User.id)

        if only_deleted:
            query = query.where(User.is_deleted == True)
        if only_active:
            query = query.where(User.is_active == True)

        results = await self.db.execute(query)
        return results.scalars().all()

    async def get_user_by_id(self,
                             user_id: int,
                             only_deleted: bool = False,
                             only_active: bool = False):
        query = select(User).where(User.id == user_id)

        if only_deleted:
            query = query.where(User.is_deleted == True)
        if only_active:
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

    async def create_user(self, data: UserCreate):
        new_user = User(username=data.username, password=data.password, email=data.email)
        self.db.add(new_user)
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        await self.db.refresh(new_user)
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

    async def update_user(self, user_model: User, update_user: dict):
        for key, value in update_user.items():
            setattr(user_model, key, value)

        await self.db.flush()
        return user_model

    async def delete_user(self, user):
        await self.db.delete(user)
        await self.db.commit()
