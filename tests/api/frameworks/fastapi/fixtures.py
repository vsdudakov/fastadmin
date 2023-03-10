import pytest
from httpx import AsyncClient as TestClient

from tests.dev.fastapi.dev import app


@pytest.fixture
def fastapi_app():
    yield app


@pytest.fixture
async def fastapi_client(fastapi_app):
    async with TestClient(app=fastapi_app, base_url="http://test/admin") as client:
        yield client
