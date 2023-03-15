from datetime import datetime

import pytest

from tests.dev.sqlalchemy import models
from tests.dev.sqlalchemy.helpers import close_connection, get_connection, init_connection


@pytest.fixture(scope="session")
async def sqlalchemy_connection():
    init_connection()
    yield get_connection()
    await close_connection()


@pytest.fixture
async def sqlalchemy_session(sqlalchemy_connection):
    async with sqlalchemy_connection() as session:
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
