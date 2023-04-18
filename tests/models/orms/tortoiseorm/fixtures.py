import pytest
from tortoise import Tortoise

from tests.environment.tortoiseorm import models
from tests.settings import DB_SQLITE


@pytest.fixture(scope="session", autouse=True)
async def tortoiseorm_session():
    await Tortoise.init(db_url=f"sqlite://{DB_SQLITE}", modules={"models": ["tests.environment.tortoiseorm.models"]})
    session = Tortoise.get_connection("default")
    yield session
    await Tortoise.close_connections()


@pytest.fixture
async def tortoiseorm_superuser():
    obj = await models.User.create(username="Test SuperUser", password="password", is_superuser=True)
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoiseorm_user():
    obj = await models.User.create(username="Test User", password="password")
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoiseorm_tournament():
    obj = await models.Tournament.create(name="Test Tournament")
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoiseorm_base_event():
    obj = await models.BaseEvent.create()
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoiseorm_event(tortoiseorm_base_event, tortoiseorm_tournament, tortoiseorm_user):
    obj = await models.Event.create(base=tortoiseorm_base_event, name="Test Event", tournament=tortoiseorm_tournament)
    await obj.participants.add(tortoiseorm_user)
    yield obj
    await obj.delete()
