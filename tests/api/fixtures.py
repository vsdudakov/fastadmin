import pytest

from fastadmin.settings import settings
from tests.api.frameworks.django.fixtures import *
from tests.api.frameworks.fastapi.fixtures import *
from tests.api.frameworks.flask.fixtures import *

frameworks = [
    "fastapi",
    "flask",
    "django",
]


@pytest.fixture(params=frameworks)
async def app(request, fastapi_app, flask_app, django_app):
    match request.param:
        case "fastapi":
            yield fastapi_app
        case "flask":
            yield flask_app
        case "django":
            yield django_app


@pytest.fixture(params=frameworks)
async def client(request, fastapi_client, flask_client, django_client):
    match request.param:
        case "fastapi":
            yield fastapi_client
        case "flask":
            yield flask_client
        case "django":
            yield django_client


@pytest.fixture
async def session_id(superuser, client):
    settings.ADMIN_USER_MODEL = superuser.__class__.__name__
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": superuser.password,
        },
    )
    assert r.status_code == 200, r.status_code
    assert not r.json(), r.json()

    yield r.cookies[settings.ADMIN_SESSION_ID_KEY]

    r = await client.post("/api/sign-out")
    assert r.status_code == 200, r.status_code
    assert not r.json(), r.json()
