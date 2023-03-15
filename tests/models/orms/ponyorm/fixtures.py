from datetime import datetime

import pytest

from tests.dev.ponyorm import models
from tests.dev.ponyorm.helpers import close_connection, get_connection, init_connection


@pytest.fixture(scope="session")
def ponyorm_connection():
    init_connection()
    yield get_connection()
    close_connection()


@pytest.fixture
def ponyorm_session(ponyorm_connection):
    yield ponyorm_connection


@pytest.fixture
def ponyorm_superuser(ponyorm_session):
    with ponyorm_session:
        obj = models.User(
            username="Test SuperUser",
            password="password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        yield obj
        obj.delete()


@pytest.fixture
def ponyorm_user(ponyorm_session):
    with ponyorm_session:
        obj = models.User(
            username="Test User",
            password="password",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        yield obj
        obj.delete()


@pytest.fixture
def ponyorm_tournament(ponyorm_session):
    with ponyorm_session:
        obj = models.Tournament(
            name="Test Tournament",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        yield obj
        obj.delete()


@pytest.fixture
def ponyorm_base_event(ponyorm_session):
    with ponyorm_session:
        obj = models.BaseEvent(
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        yield obj
        obj.delete()


@pytest.fixture
def ponyorm_event(ponyorm_session, ponyorm_base_event, ponyorm_tournament, ponyorm_user):
    with ponyorm_session:
        obj = models.Event(
            base=ponyorm_base_event,
            name="Test Event",
            tournament=ponyorm_tournament,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        obj.participants.add(ponyorm_user)
        yield obj
        obj.delete()
