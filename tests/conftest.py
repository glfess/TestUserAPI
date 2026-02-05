if False:
    #WIP
    import asyncio
    import pytest
    import pytest_asyncio
    from httpx import AsyncClient, ASGITransport
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.models.user import Base
    from app.main import app

    engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

    AsyncSessionLocal = sessionmaker(bind=engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False
                                 )


    @pytest_asyncio.fixture(scope="session")
    async def engine():
        engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
        yield engine
        await engine.dispose()

    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def prepare_db(engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest_asyncio.fixture(scope="function")
    async def db_session(engine):
        async with AsyncSessionLocal() as session:
            yield session

    @pytest_asyncio.fixture(scope="function")
    async def client():
        async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test"
                           ) as ac:
            yield ac