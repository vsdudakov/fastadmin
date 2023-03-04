import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient as TestClient

from fastadmin.app import admin_app
from tests.tortoise.helpers import (
    tortoise_close_db_connection,
    tortoise_create_objects,
    tortoise_delete_objects,
    tortoise_init_db_connection,
)


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
async def fastapi_app() -> AsyncGenerator:
    yield admin_app


@pytest.fixture(scope="session", autouse=True)
async def db():
    tortoise_connection = await tortoise_init_db_connection()
    yield {
        "tortoise": tortoise_connection,
    }
    await tortoise_close_db_connection()


@pytest.fixture
async def client(fastapi_app) -> AsyncGenerator:
    async with TestClient(app=fastapi_app, base_url="http://test") as client:
        yield client


@pytest.fixture(
    params=[
        "tortoise",
    ],
)
async def objects(request):
    match request.param:
        case "tortoise":
            objs = await tortoise_create_objects()
            yield objs
            await tortoise_delete_objects()
        case _:
            objs = await tortoise_create_objects()
            yield objs
            await tortoise_delete_objects()
