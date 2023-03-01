import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient as TestClient

from fastadmin.settings import settings
from fastadmin.app import admin_app


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
async def fastapi_app() -> AsyncGenerator:
    yield admin_app


@pytest.fixture
async def client(fastapi_app) -> AsyncGenerator:
    async with TestClient(app=fastapi_app, base_url="http://test") as client:
        yield client
