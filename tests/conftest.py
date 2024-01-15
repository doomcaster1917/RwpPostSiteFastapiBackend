import asyncio
import pytest
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from redis import asyncio as aioredis
from fastapi import WebSocket
import aiofiles
import os
from src.routers.aioSMTP import send_mail_async
from src.database import get_db
from src.database import Base

from src.config import (DB_HOST_TEST, DB_NAME_TEST, DB_PASS_TEST, DB_PORT_TEST,
                        DB_USER_TEST)
from src.main import app

DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}/{DB_NAME_TEST}"

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
Base.metadata.bind = engine_test
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)



async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def switch_off_email_sending(*args, **kwargs):
    #This func is needed to save e-mail sender address from spam-ban during tests
    pass

app.dependency_overrides[get_db] = override_get_async_session
app.dependency_overrides[send_mail_async] = switch_off_email_sending

@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def redis_server() -> aioredis.Redis:
    redis = await aioredis.Redis(host='localhost', port=6379, decode_responses=True)
    yield redis
    await redis.close()

@pytest.fixture(scope="session")
async def test_user_info() -> dict:
    email = "testcase@gmail.com"
    password = "testcase"
    nickname = "testcase"
    user_info = {"email": email, "password": password, "nickname": nickname}
    yield user_info

@pytest.fixture(scope="session")
async def picture_binary() -> bytes:
    if os.path.isfile(f"{os.getcwd()}/tests/static/test_picture.png"):
        async with aiofiles.open(f"{os.getcwd()}/tests/static/test_picture.png", "rb") as content:
            yield bytes(await content.read())


