import pytest
from asgiref.wsgi import WsgiToAsgi
from httpx import AsyncClient as TestClient

from fastadmin.api.frameworks.flask.dev import app


@pytest.fixture
def flask_app():
    yield WsgiToAsgi(app)


@pytest.fixture
async def flask_client(flask_app):
    async with TestClient(app=flask_app, base_url="http://test/admin") as client:
        yield client
