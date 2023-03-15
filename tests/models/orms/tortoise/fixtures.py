import pytest

from tests.dev.tortoise import models
from tests.dev.tortoise.helpers import close_connection, get_connection, init_connection


@pytest.fixture(scope="session")
async def tortoise_connection():
    await init_connection()
    yield get_connection()
    await close_connection()


@pytest.fixture
async def tortoise_session(tortoise_connection):
    yield tortoise_connection


@pytest.fixture
async def tortoise_superuser(tortoise_session):
    obj = await models.User.create(username="Test SuperUser", password="password", is_superuser=True)
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoise_user(tortoise_session):
    obj = await models.User.create(username="Test User", password="password")
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoise_tournament(tortoise_session):
    obj = await models.Tournament.create(name="Test Tournament")
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoise_base_event(tortoise_session):
    obj = await models.BaseEvent.create()
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoise_event(tortoise_base_event, tortoise_tournament, tortoise_user):
    obj = await models.Event.create(base=tortoise_base_event, name="Test Event", tournament=tortoise_tournament)
    await obj.participants.add(tortoise_user)
    yield obj
    await obj.delete()
