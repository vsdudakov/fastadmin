import pytest
from httpx import AsyncClient as TestClient

from tests.environment.django.dev.dev.asgi import application


@pytest.fixture
def django_app():
    yield application


@pytest.fixture
async def django_client(django_app):
    async with TestClient(app=django_app, base_url="http://test/admin") as client:
        yield client
