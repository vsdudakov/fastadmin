from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient as TestClient

from fastadmin.api.fastapi.app import app


@pytest.fixture
async def fastapi_app() -> AsyncGenerator:
    yield app


@pytest.fixture
async def fastapi_client(fastapi_app) -> AsyncGenerator:
    async with TestClient(app=fastapi_app, base_url="http://test") as client:
        yield client
