import asyncio
from copy import copy
from datetime import datetime, timezone
from enum import Enum

import django
import pytest
from asgiref.wsgi import WsgiToAsgi
from django.db import connections
from httpx import AsyncClient as TestClient
from pony.orm import commit, db_session
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from tortoise import Tortoise

from fastadmin.models.base import admin_models as admin_models_objs
from fastadmin.models.helpers import get_admin_model
from fastadmin.settings import settings
from tests.environment.django.dev.dev.asgi import application as django_application
from tests.environment.djangoorm import models as django_models
from tests.environment.fastapi.dev import app as fastapi_application
from tests.environment.flask.dev import app as flask_application
from tests.environment.ponyorm import models as ponyorm_models
from tests.environment.sqlalchemy import models as sqlalchemy_models
from tests.environment.tortoiseorm import models as tortoiseorm_models
from tests.settings import DB_SQLITE, FRAMEWORKS, ORMS


@pytest.fixture(scope="session", autouse=True)
def django_session():
    django.setup(set_prefix=False)
    session = connections["default"]
    return session


@pytest.fixture()
def django_superuser():
    obj = django_models.User.objects.create(username="Test SuperUser", password="password", is_superuser=True)
    yield obj
    obj.delete()


@pytest.fixture()
def django_user():
    obj = django_models.User.objects.create(username="Test User", password="password")
    yield obj
    obj.delete()


@pytest.fixture()
def django_tournament():
    obj = django_models.Tournament.objects.create(name="Test Tournament")
    yield obj
    obj.delete()


@pytest.fixture()
def django_base_event():
    obj = django_models.BaseEvent.objects.create()
    yield obj
    obj.delete()


@pytest.fixture()
def django_event(django_base_event, django_tournament, django_user):
    obj = django_models.Event.objects.create(base=django_base_event, name="Test Event", tournament=django_tournament)
    obj.participants.add(django_user)
    yield obj
    obj.delete()


@pytest.fixture(scope="session", autouse=True)
def ponyorm_session():
    ponyorm_models.db.bind(provider="sqlite", filename=DB_SQLITE, create_db=False)
    ponyorm_models.db.provider.converter_classes.append((Enum, ponyorm_models.EnumConverter))
    ponyorm_models.db.generate_mapping()

    with db_session:
        yield db_session


@pytest.fixture()
def ponyorm_superuser():
    obj = ponyorm_models.User(
        username="Test SuperUser",
        password="password",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    commit()
    yield obj
    obj.delete()


@pytest.fixture()
def ponyorm_user():
    obj = ponyorm_models.User(
        username="Test User",
        password="password",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    commit()
    yield obj
    obj.delete()


@pytest.fixture()
def ponyorm_tournament():
    obj = ponyorm_models.Tournament(
        name="Test Tournament",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    commit()
    yield obj
    obj.delete()


@pytest.fixture()
def ponyorm_base_event():
    obj = ponyorm_models.BaseEvent(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    commit()
    yield obj
    obj.delete()


@pytest.fixture()
def ponyorm_event(ponyorm_base_event, ponyorm_tournament, ponyorm_user):
    obj = ponyorm_models.Event(
        base=ponyorm_base_event,
        name="Test Event",
        tournament=ponyorm_tournament,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    commit()
    obj.participants.add(ponyorm_user)
    commit()
    yield obj
    obj.delete()


@pytest.fixture(scope="session", autouse=True)
async def sqlalchemy_session():
    sqlalchemy_engine = create_async_engine(
        f"sqlite+aiosqlite:///{DB_SQLITE}",
        echo=True,
    )
    sqlalchemy_sessionmaker = async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)
    for model in (
        sqlalchemy_models.User,
        sqlalchemy_models.Tournament,
        sqlalchemy_models.BaseEvent,
        sqlalchemy_models.Event,
    ):
        admin_model = get_admin_model(model)
        assert admin_model
        admin_model.set_sessionmaker(sqlalchemy_sessionmaker)

    async with sqlalchemy_sessionmaker() as session:
        yield session


@pytest.fixture()
async def sqlalchemy_superuser(sqlalchemy_session):
    obj = sqlalchemy_models.User(
        username="Test SuperUser",
        password="password",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)

    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture()
async def sqlalchemy_user(sqlalchemy_session):
    obj = sqlalchemy_models.User(
        username="Test User",
        password="password",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)
    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture()
async def sqlalchemy_tournament(sqlalchemy_session):
    obj = sqlalchemy_models.Tournament(
        name="Test Tournament",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)
    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture()
async def sqlalchemy_base_event(sqlalchemy_session):
    obj = sqlalchemy_models.BaseEvent(
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)
    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture()
async def sqlalchemy_event(sqlalchemy_session, sqlalchemy_base_event, sqlalchemy_tournament, sqlalchemy_user):
    obj = sqlalchemy_models.Event(
        base=sqlalchemy_base_event,
        name="Test Event",
        tournament=sqlalchemy_tournament,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    obj.participants.append(sqlalchemy_user)
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)
    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture(scope="session", autouse=True)
async def tortoiseorm_session():
    await Tortoise.init(db_url=f"sqlite://{DB_SQLITE}", modules={"models": ["tests.environment.tortoiseorm.models"]})
    session = Tortoise.get_connection("default")
    yield session
    await Tortoise.close_connections()


@pytest.fixture()
async def tortoiseorm_superuser():
    obj = await tortoiseorm_models.User.create(username="Test SuperUser", password="password", is_superuser=True)
    yield obj
    await obj.delete()


@pytest.fixture()
async def tortoiseorm_user():
    obj = await tortoiseorm_models.User.create(username="Test User", password="password")
    yield obj
    await obj.delete()


@pytest.fixture()
async def tortoiseorm_tournament():
    obj = await tortoiseorm_models.Tournament.create(name="Test Tournament")
    yield obj
    await obj.delete()


@pytest.fixture()
async def tortoiseorm_base_event():
    obj = await tortoiseorm_models.BaseEvent.create()
    yield obj
    await obj.delete()


@pytest.fixture()
async def tortoiseorm_event(tortoiseorm_base_event, tortoiseorm_tournament, tortoiseorm_user):
    obj = await tortoiseorm_models.Event.create(
        base=tortoiseorm_base_event, name="Test Event", tournament=tortoiseorm_tournament
    )
    await obj.participants.add(tortoiseorm_user)
    yield obj
    await obj.delete()


@pytest.fixture(params=ORMS)
async def superuser(request, tortoiseorm_superuser, django_superuser, sqlalchemy_superuser, ponyorm_superuser):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_superuser
        case "djangoorm":
            yield django_superuser
        case "sqlalchemy":
            yield sqlalchemy_superuser
        case "ponyorm":
            yield ponyorm_superuser


@pytest.fixture(params=ORMS)
async def user(request, tortoiseorm_user, django_user, sqlalchemy_user, ponyorm_user):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_user
        case "djangoorm":
            yield django_user
        case "sqlalchemy":
            yield sqlalchemy_user
        case "ponyorm":
            yield ponyorm_user


@pytest.fixture(params=ORMS)
async def tournament(request, tortoiseorm_tournament, django_tournament, sqlalchemy_tournament, ponyorm_tournament):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_tournament
        case "djangoorm":
            yield django_tournament
        case "sqlalchemy":
            yield sqlalchemy_tournament
        case "ponyorm":
            yield ponyorm_tournament


@pytest.fixture(params=ORMS)
async def base_event(request, tortoiseorm_base_event, django_base_event, sqlalchemy_base_event, ponyorm_base_event):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_base_event
        case "djangoorm":
            yield django_base_event
        case "sqlalchemy":
            yield sqlalchemy_base_event
        case "ponyorm":
            yield ponyorm_base_event


@pytest.fixture(params=ORMS)
async def event(request, tortoiseorm_event, django_event, sqlalchemy_event, ponyorm_event):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_event
        case "djangoorm":
            yield django_event
        case "sqlalchemy":
            yield sqlalchemy_event
        case "ponyorm":
            yield ponyorm_event


@pytest.fixture()
async def admin_models():
    prev_admin_models = {k: copy(v) for k, v in admin_models_objs.items()}
    yield admin_models_objs
    for k, v in prev_admin_models.items():
        admin_models_objs[k] = v


@pytest.fixture()
def django_app():
    return django_application


@pytest.fixture()
async def django_client(django_app):
    async with TestClient(app=django_app, base_url="http://test/admin") as client:
        yield client


@pytest.fixture()
def fastapi_app():
    return fastapi_application


@pytest.fixture()
async def fastapi_client(fastapi_app):
    async with TestClient(app=fastapi_app, base_url="http://test/admin") as client:
        yield client


@pytest.fixture()
def flask_app():
    return WsgiToAsgi(flask_application)


@pytest.fixture()
async def flask_client(flask_app):
    async with TestClient(app=flask_app, base_url="http://test/admin") as client:
        yield client


@pytest.fixture(params=FRAMEWORKS)
async def app(request, fastapi_app, flask_app, django_app):
    match request.param:
        case "fastapi":
            yield fastapi_app
        case "flask":
            yield flask_app
        case "django":
            yield django_app


@pytest.fixture(params=FRAMEWORKS)
async def client(request, fastapi_client, flask_client, django_client):
    match request.param:
        case "fastapi":
            yield fastapi_client
        case "flask":
            yield flask_client
        case "django":
            yield django_client


@pytest.fixture()
async def session_id(superuser, client):
    settings.ADMIN_USER_MODEL = superuser.get_model_name()
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": superuser.password,
        },
    )
    assert r.status_code == 200, r.text
    assert not r.json(), r.json()

    yield r.cookies[settings.ADMIN_SESSION_ID_KEY]

    r = await client.post("/api/sign-out")
    assert r.status_code == 200, r.text
    assert not r.json(), r.json()


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()
