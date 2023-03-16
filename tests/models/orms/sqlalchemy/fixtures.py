from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from examples.sqlalchemy import models
from fastadmin.models.helpers import get_admin_model
from tests.settings import DB_SQLITE


@pytest.fixture(scope="session", autouse=True)
async def sqlalchemy_session():
    sqlalchemy_engine = create_async_engine(
        f"sqlite+aiosqlite:///{DB_SQLITE}",
        echo=True,
    )
    sqlalchemy_sessionmaker = async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)
    for model in (models.User, models.Tournament, models.BaseEvent, models.Event):
        admin_model = get_admin_model(model)
        assert admin_model
        admin_model.set_sessionmaker(sqlalchemy_sessionmaker)

    async with sqlalchemy_sessionmaker() as session:
        yield session


@pytest.fixture
async def sqlalchemy_superuser(sqlalchemy_session):
    obj = models.User(
        username="Test SuperUser",
        password="password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)

    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture
async def sqlalchemy_user(sqlalchemy_session):
    obj = models.User(
        username="Test User",
        password="password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)
    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture
async def sqlalchemy_tournament(sqlalchemy_session):
    obj = models.Tournament(
        name="Test Tournament",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)
    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture
async def sqlalchemy_base_event(sqlalchemy_session):
    obj = models.BaseEvent(
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)
    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()


@pytest.fixture
async def sqlalchemy_event(sqlalchemy_session, sqlalchemy_base_event, sqlalchemy_tournament, sqlalchemy_user):
    obj = models.Event(
        base=sqlalchemy_base_event,
        name="Test Event",
        tournament=sqlalchemy_tournament,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    obj.participants.append(sqlalchemy_user)
    sqlalchemy_session.add(obj)
    await sqlalchemy_session.commit()
    await sqlalchemy_session.refresh(obj)
    yield obj
    await sqlalchemy_session.delete(obj)
    await sqlalchemy_session.commit()
