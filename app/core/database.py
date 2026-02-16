from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL,
                             echo=False,
                             pool_size=10,
                             max_overflow=20,
                             pool_timeout=30,
                             pool_recycle=3600
                             )

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session_maker(bind=engine) as session:
        yield session
