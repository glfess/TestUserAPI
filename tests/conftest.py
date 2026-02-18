import os

os.environ.setdefault("PYTEST", "1")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis_service, get_redis_client
from app.core.redis_service import RedisCacheService
from app.models.user import Base
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

@pytest_asyncio.fixture
async def engine():
    _engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
    yield _engine
    await _engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def prepare_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(engine, prepare_db):
    async with async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )() as session:
        yield session

@pytest_asyncio.fixture
async def redis_client():
    import redis.asyncio as redis
    pool = redis.ConnectionPool.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True
    )
    client = redis.Redis(connection_pool=pool)

    yield client
    await client.aclose()
    await pool.disconnect()

@pytest_asyncio.fixture(autouse=True)
async def flush_redis(redis_client):
    yield
    await redis_client.flushdb()

@pytest_asyncio.fixture
async def client(db_session, redis_client):
    async def override_get_db():
        yield db_session

    async def override_get_redis_client():
        yield redis_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis_client

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
