import asyncio
from copy import copy
from datetime import datetime, timezone

import pytest
from asgiref.sync import sync_to_async
from asgiref.wsgi import WsgiToAsgi
from django.core.management import call_command
from django.db import connections
from httpx import AsyncClient as TestClient
from pony.orm import commit, db_session
from pony.orm.core import BindingError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from tortoise import Tortoise

from fastadmin import DjangoModelAdmin, PonyORMModelAdmin, SqlAlchemyModelAdmin, TortoiseModelAdmin
from fastadmin.models.base import admin_models as admin_models_objs
from fastadmin.models.helpers import get_admin_model
from fastadmin.settings import settings
from tests.settings import FRAMEWORKS, ORMS


@pytest.fixture(scope="session")
async def django_session():
    async def _django_session():
        # await sync_to_async(call_command)('makemigrations', 'djangoorm')
        await sync_to_async(call_command)("migrate")

        session = connections["default"]
        yield session, "djangoorm"

    return _django_session


@pytest.fixture()
async def django_superuser():
    async def _django_superuser():
        from tests.environment.django.orm import models as django_models

        obj = await sync_to_async(django_models.User.objects.create)(
            username="Test SuperUser", password="password", is_superuser=True
        )
        yield obj
        await sync_to_async(obj.delete)()

    return _django_superuser


@pytest.fixture()
async def django_user():
    async def _django_user():
        from tests.environment.django.orm import models as django_models

        obj = await sync_to_async(django_models.User.objects.create)(username="Test User", password="password")
        yield obj
        await sync_to_async(obj.delete)()

    return _django_user


@pytest.fixture()
async def django_tournament():
    async def _django_tournament():
        from tests.environment.django.orm import models as django_models

        obj = await sync_to_async(django_models.Tournament.objects.create)(name="Test Tournament")
        yield obj
        await sync_to_async(obj.delete)()

    return _django_tournament


@pytest.fixture()
async def django_base_event():
    async def _django_base_event():
        from tests.environment.django.orm import models as django_models

        obj = await sync_to_async(django_models.BaseEvent.objects.create)()
        yield obj
        await sync_to_async(obj.delete)()

    return _django_base_event


@pytest.fixture()
async def django_event():
    async def django_event():
        from tests.environment.django.orm import models as django_models

        django_base_event = await sync_to_async(django_models.BaseEvent.objects.create)()
        django_tournament = await sync_to_async(django_models.Tournament.objects.create)(name="Test Tournament")
        django_user = await sync_to_async(django_models.User.objects.create)(username="Test User", password="password")
        obj = await sync_to_async(django_models.Event.objects.create)(
            base=django_base_event, name="Test Event", tournament=django_tournament
        )
        await sync_to_async(obj.participants.add)(django_user)
        yield obj
        await sync_to_async(obj.delete)()
        await sync_to_async(django_user.delete)()
        await sync_to_async(django_base_event.delete)()
        await sync_to_async(django_tournament.delete)()

    return django_event


@pytest.fixture(scope="session")
async def ponyorm_session():
    async def _ponyorm_session():
        from enum import Enum

        from tests.environment.ponyorm import models as ponyorm_models

        try:  # noqa: SIM105
            ponyorm_models.db.bind(provider="sqlite", filename=":sharedmemory:", create_db=True)
        except BindingError:
            # Database is already bound
            pass
        ponyorm_models.db.provider.converter_classes.append((Enum, ponyorm_models.EnumConverter))
        try:  # noqa: SIM105
            ponyorm_models.db.generate_mapping(create_tables=True)
        except BindingError:
            # Mapping was already generated
            pass

        with db_session:
            yield db_session, "ponyorm"

    return _ponyorm_session


@pytest.fixture()
async def ponyorm_superuser():
    async def _ponyorm_superuser():
        from tests.environment.ponyorm import models as ponyorm_models

        obj = ponyorm_models.User(
            username="Test SuperUser",
            password="password",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_superuser=True,
        )
        commit()
        yield obj
        obj.delete()

    return _ponyorm_superuser


@pytest.fixture()
async def ponyorm_user():
    async def _ponyorm_user():
        from tests.environment.ponyorm import models as ponyorm_models

        obj = ponyorm_models.User(
            username="Test User",
            password="password",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        commit()
        yield obj
        obj.delete()

    return _ponyorm_user


@pytest.fixture()
async def ponyorm_tournament():
    async def _ponyorm_tournament():
        from tests.environment.ponyorm import models as ponyorm_models

        obj = ponyorm_models.Tournament(
            name="Test Tournament",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        commit()
        yield obj
        obj.delete()

    return _ponyorm_tournament


@pytest.fixture()
async def ponyorm_base_event():
    async def _ponyorm_base_event():
        from tests.environment.ponyorm import models as ponyorm_models

        obj = ponyorm_models.BaseEvent(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        commit()
        yield obj
        obj.delete()

    return _ponyorm_base_event


@pytest.fixture()
async def ponyorm_event():
    async def _ponyorm_event():
        from tests.environment.ponyorm import models as ponyorm_models

        ponyorm_base_event = ponyorm_models.BaseEvent(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        ponyorm_tournament = ponyorm_models.Tournament(
            name="Test Tournament",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        ponyorm_user = ponyorm_models.User(
            username="Test User",
            password="password",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
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
        ponyorm_user.delete()
        ponyorm_base_event.delete()
        ponyorm_tournament.delete()

    return _ponyorm_event


@pytest.fixture(scope="session")
async def sqlalchemy_session():
    async def _sqlalchemy_session():
        from tests.environment.sqlalchemy import models as sqlalchemy_models

        sqlalchemy_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=True,
        )
        sqlalchemy_sessionmaker = async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)
        async with sqlalchemy_engine.begin() as c:
            await c.run_sync(sqlalchemy_models.Base.metadata.drop_all)
            await c.run_sync(sqlalchemy_models.Base.metadata.create_all)
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
            yield session, "sqlalchemy"

    return _sqlalchemy_session


@pytest.fixture()
async def sqlalchemy_superuser():
    async def _sqlalchemy_superuser(sqlalchemy_session):
        from tests.environment.sqlalchemy import models as sqlalchemy_models

        obj = sqlalchemy_models.User(
            username="Test SuperUser",
            password="password",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_superuser=True,
        )
        sqlalchemy_session.add(obj)
        await sqlalchemy_session.commit()
        await sqlalchemy_session.refresh(obj)

        yield obj

        await sqlalchemy_session.delete(obj)
        await sqlalchemy_session.commit()

    return _sqlalchemy_superuser


@pytest.fixture()
async def sqlalchemy_user():
    async def _sqlalchemy_user(sqlalchemy_session):
        from tests.environment.sqlalchemy import models as sqlalchemy_models

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

    return _sqlalchemy_user


@pytest.fixture()
async def sqlalchemy_tournament():
    async def _sqlalchemy_tournament(sqlalchemy_session):
        from tests.environment.sqlalchemy import models as sqlalchemy_models

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

    return _sqlalchemy_tournament


@pytest.fixture()
async def sqlalchemy_base_event():
    async def sqlalchemy_base_event(sqlalchemy_session):
        from tests.environment.sqlalchemy import models as sqlalchemy_models

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

    return sqlalchemy_base_event


@pytest.fixture()
async def sqlalchemy_event():
    async def _sqlalchemy_event(sqlalchemy_session):
        from tests.environment.sqlalchemy import models as sqlalchemy_models

        sqlalchemy_base_event = sqlalchemy_models.BaseEvent(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        sqlalchemy_tournament = sqlalchemy_models.Tournament(
            name="Test Tournament",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        sqlalchemy_user = sqlalchemy_models.User(
            username="Test User",
            password="password",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
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
        await sqlalchemy_session.refresh(sqlalchemy_user)
        await sqlalchemy_session.refresh(sqlalchemy_base_event)
        await sqlalchemy_session.refresh(sqlalchemy_tournament)

        yield obj
        await sqlalchemy_session.delete(obj)
        await sqlalchemy_session.delete(sqlalchemy_user)
        await sqlalchemy_session.delete(sqlalchemy_base_event)
        await sqlalchemy_session.delete(sqlalchemy_tournament)
        await sqlalchemy_session.commit()

    return _sqlalchemy_event


@pytest.fixture(scope="session")
async def tortoiseorm_session():
    async def _tortoiseorm_session():
        await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["tests.environment.tortoiseorm.models"]})
        await Tortoise.generate_schemas()

        session = Tortoise.get_connection("default")
        yield session, "tortoiseorm"
        await Tortoise.close_connections()

    return _tortoiseorm_session


@pytest.fixture()
async def tortoiseorm_superuser():
    async def _tortoiseorm_superuser():
        from tests.environment.tortoiseorm import models as tortoiseorm_models

        obj = await tortoiseorm_models.User.create(username="Test SuperUser", password="password", is_superuser=True)
        yield obj
        await obj.delete()

    return _tortoiseorm_superuser


@pytest.fixture()
async def tortoiseorm_user():
    async def _tortoiseorm_user():
        from tests.environment.tortoiseorm import models as tortoiseorm_models

        obj = await tortoiseorm_models.User.create(username="Test User", password="password")
        yield obj
        await obj.delete()

    return _tortoiseorm_user


@pytest.fixture()
async def tortoiseorm_tournament():
    async def _tortoiseorm_tournament():
        from tests.environment.tortoiseorm import models as tortoiseorm_models

        obj = await tortoiseorm_models.Tournament.create(name="Test Tournament")
        yield obj
        await obj.delete()

    return _tortoiseorm_tournament


@pytest.fixture()
async def tortoiseorm_base_event():
    async def _tortoiseorm_base_event():
        from tests.environment.tortoiseorm import models as tortoiseorm_models

        obj = await tortoiseorm_models.BaseEvent.create()
        yield obj
        await obj.delete()

    return _tortoiseorm_base_event


@pytest.fixture()
async def tortoiseorm_event():
    async def _tortoiseorm_event():
        from tests.environment.tortoiseorm import models as tortoiseorm_models

        tortoiseorm_base_event = await tortoiseorm_models.BaseEvent.create()
        tortoiseorm_tournament = await tortoiseorm_models.Tournament.create(name="Test Tournament")
        tortoiseorm_user = await tortoiseorm_models.User.create(username="Test User", password="password")
        obj = await tortoiseorm_models.Event.create(
            base=tortoiseorm_base_event, name="Test Event", tournament=tortoiseorm_tournament
        )
        await obj.participants.add(tortoiseorm_user)
        yield obj
        await obj.delete()
        await tortoiseorm_user.delete()
        await tortoiseorm_user.delete()
        await tortoiseorm_base_event.delete()

    return _tortoiseorm_event


@pytest.fixture(params=ORMS, autouse=True)
async def session_with_type(request, tortoiseorm_session, django_session, sqlalchemy_session, ponyorm_session):
    match request.param:
        case "tortoiseorm":
            async for session in tortoiseorm_session():
                yield session
        case "djangoorm":
            async for session in django_session():
                yield session
        case "sqlalchemy":
            async for session in sqlalchemy_session():
                yield session
        case "ponyorm":
            async for session in ponyorm_session():
                yield session


@pytest.fixture()
async def superuser(
    session_with_type, tortoiseorm_superuser, django_superuser, sqlalchemy_superuser, ponyorm_superuser
):
    session, session_type = session_with_type
    match session_type:
        case "tortoiseorm":
            async for obj in tortoiseorm_superuser():
                yield obj
        case "djangoorm":
            async for obj in django_superuser():
                yield obj
        case "sqlalchemy":
            async for obj in sqlalchemy_superuser(session):
                yield obj
        case "ponyorm":
            async for obj in ponyorm_superuser():
                yield obj


@pytest.fixture()
async def user(session_with_type, tortoiseorm_user, django_user, sqlalchemy_user, ponyorm_user):
    session, session_type = session_with_type
    match session_type:
        case "tortoiseorm":
            async for obj in tortoiseorm_user():
                yield obj
        case "djangoorm":
            async for obj in django_user():
                yield obj
        case "sqlalchemy":
            async for obj in sqlalchemy_user(session):
                yield obj
        case "ponyorm":
            async for obj in ponyorm_user():
                yield obj


@pytest.fixture()
async def tournament(
    session_with_type, tortoiseorm_tournament, django_tournament, sqlalchemy_tournament, ponyorm_tournament
):
    session, session_type = session_with_type
    match session_type:
        case "tortoiseorm":
            async for obj in tortoiseorm_tournament():
                yield obj
        case "djangoorm":
            async for obj in django_tournament():
                yield obj
        case "sqlalchemy":
            async for obj in sqlalchemy_tournament(session):
                yield obj
        case "ponyorm":
            async for obj in ponyorm_tournament():
                yield obj


@pytest.fixture()
async def base_event(
    session_with_type, tortoiseorm_base_event, django_base_event, sqlalchemy_base_event, ponyorm_base_event
):
    session, session_type = session_with_type
    match session_type:
        case "tortoiseorm":
            async for obj in tortoiseorm_base_event():
                yield obj
        case "djangoorm":
            async for obj in django_base_event():
                yield obj
        case "sqlalchemy":
            async for obj in sqlalchemy_base_event(session):
                yield obj
        case "ponyorm":
            async for obj in ponyorm_base_event():
                yield obj


@pytest.fixture()
async def event(session_with_type, tortoiseorm_event, django_event, sqlalchemy_event, ponyorm_event):
    session, session_type = session_with_type
    match session_type:
        case "tortoiseorm":
            async for obj in tortoiseorm_event():
                yield obj
        case "djangoorm":
            async for obj in django_event():
                yield obj
        case "sqlalchemy":
            async for obj in sqlalchemy_event(session):
                yield obj
        case "ponyorm":
            async for obj in ponyorm_event():
                yield obj


@pytest.fixture()
async def base_model_admin(session_with_type):
    _, session_type = session_with_type
    match session_type:
        case "tortoiseorm":
            yield TortoiseModelAdmin
        case "djangoorm":
            yield DjangoModelAdmin
        case "sqlalchemy":
            yield SqlAlchemyModelAdmin
        case "ponyorm":
            yield PonyORMModelAdmin


@pytest.fixture()
async def admin_models():
    prev_admin_models = {k: copy(v) for k, v in admin_models_objs.items()}
    yield admin_models_objs
    for k, v in prev_admin_models.items():
        admin_models_objs[k] = v


@pytest.fixture(params=FRAMEWORKS)
async def app(request):
    match request.param:
        case "fastapi":
            from tests.environment.fastapi.dev import app as fastapi_application

            yield fastapi_application
        case "flask":
            from tests.environment.flask.dev import app as flask_application

            yield WsgiToAsgi(flask_application)
        case "django":
            from tests.environment.django.dev.asgi import application as django_application

            yield django_application


@pytest.fixture()
async def client(app):
    async with TestClient(app=app, base_url="http://test/admin") as client:
        yield client


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
