import pytest
from httpx import AsyncClient


@pytest.fixture
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url='http://test') as app:
        yield app