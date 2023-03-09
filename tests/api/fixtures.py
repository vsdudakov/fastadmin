import pytest
from httpx import Client as SyncClient

from tests.api.frameworks.fastapi.fixtures import *
from tests.api.frameworks.flask.fixtures import *

from fastadmin import register_admin_model_class, unregister_admin_model_class
from fastadmin.api.schemas import SignInInputSchema
from fastadmin.api.service import ApiService
from tests.models.orms.tortoise.admins import UserModelAdmin

frameworks = ["fastapi", "flask"]

@pytest.fixture(params=frameworks)
async def app(request, fastapi_app, flask_app):
    match request.param:
        case "fastapi":
            yield fastapi_app
        case "flask":
            yield flask_app


@pytest.fixture(params=frameworks)
async def client(request, fastapi_client, flask_client):
    match request.param:
        case "fastapi":
            yield fastapi_client
        case "flask":
            yield flask_client


@pytest.fixture
async def session_id(superuser):
    service = ApiService()
    payload = SignInInputSchema(
        username=superuser.username,
        password=superuser.password,
    )
    register_admin_model_class(UserModelAdmin, [superuser.__class__])
    session_id = await service.sign_in(None, payload)
    yield session_id
    await service.sign_out(session_id)
    unregister_admin_model_class([superuser.__class__])
