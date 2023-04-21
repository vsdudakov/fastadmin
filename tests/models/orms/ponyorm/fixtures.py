from datetime import datetime
from enum import Enum

import pytest
from pony.orm import commit, db_session

from tests.environment.ponyorm import models
from tests.settings import DB_SQLITE


@pytest.fixture(scope="session", autouse=True)
def ponyorm_session():
    models.db.bind(provider="sqlite", filename=DB_SQLITE, create_db=False)
    models.db.provider.converter_classes.append((Enum, models.EnumConverter))
    models.db.generate_mapping()

    with db_session:
        yield db_session


@pytest.fixture
def ponyorm_superuser():
    obj = models.User(
        username="Test SuperUser",
        password="password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    commit()
    yield obj
    obj.delete()


@pytest.fixture
def ponyorm_user():
    obj = models.User(
        username="Test User",
        password="password",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    commit()
    yield obj
    obj.delete()


@pytest.fixture
def ponyorm_tournament():
    obj = models.Tournament(
        name="Test Tournament",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    commit()
    yield obj
    obj.delete()


@pytest.fixture
def ponyorm_base_event():
    obj = models.BaseEvent(
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    commit()
    yield obj
    obj.delete()


@pytest.fixture
def ponyorm_event(ponyorm_base_event, ponyorm_tournament, ponyorm_user):
    obj = models.Event(
        base=ponyorm_base_event,
        name="Test Event",
        tournament=ponyorm_tournament,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    commit()
    obj.participants.add(ponyorm_user)
    commit()
    yield obj
    obj.delete()
