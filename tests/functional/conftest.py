from typing import AsyncGenerator
from app.main import app as fastapi_app
import pytest
from httpx import AsyncClient


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url='http://test') as app:
        yield app