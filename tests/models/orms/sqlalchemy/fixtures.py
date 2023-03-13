from datetime import datetime

import pytest

from tests.dev.sqlalchemy import models


@pytest.fixture(scope="session")
async def sqlalchemy_connection():
    yield models.sqlalchemy_session


@pytest.fixture
async def sqlalchemy_db(sqlalchemy_connection):
    async with sqlalchemy_connection() as session:
        yield session


@pytest.fixture
async def sqlalchemy_superuser(sqlalchemy_db):
    obj = models.User(
        username="Test SuperUser",
        password="password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sqlalchemy_db.add(obj)
    await sqlalchemy_db.commit()
    await sqlalchemy_db.refresh(obj)

    yield obj
    await sqlalchemy_db.delete(obj)
    await sqlalchemy_db.commit()


@pytest.fixture
async def sqlalchemy_user(sqlalchemy_db):
    obj = models.User(
        username="Test User",
        password="password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sqlalchemy_db.add(obj)
    await sqlalchemy_db.commit()
    await sqlalchemy_db.refresh(obj)
    yield obj
    await sqlalchemy_db.delete(obj)
    await sqlalchemy_db.commit()


@pytest.fixture
async def sqlalchemy_tournament(sqlalchemy_db):
    obj = models.Tournament(
        name="Test Tournament",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sqlalchemy_db.add(obj)
    await sqlalchemy_db.commit()
    await sqlalchemy_db.refresh(obj)
    yield obj
    await sqlalchemy_db.delete(obj)
    await sqlalchemy_db.commit()


@pytest.fixture
async def sqlalchemy_base_event(sqlalchemy_db):
    obj = models.BaseEvent(
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    sqlalchemy_db.add(obj)
    await sqlalchemy_db.commit()
    await sqlalchemy_db.refresh(obj)
    yield obj
    await sqlalchemy_db.delete(obj)
    await sqlalchemy_db.commit()


@pytest.fixture
async def sqlalchemy_event(sqlalchemy_db, sqlalchemy_base_event, sqlalchemy_tournament, sqlalchemy_user):
    obj = models.Event(
        base=sqlalchemy_base_event,
        name="Test Event",
        tournament=sqlalchemy_tournament,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    obj.participants.append(sqlalchemy_user)
    sqlalchemy_db.add(obj)
    await sqlalchemy_db.commit()
    await sqlalchemy_db.refresh(obj)
    yield obj
    await sqlalchemy_db.delete(obj)
    await sqlalchemy_db.commit()
