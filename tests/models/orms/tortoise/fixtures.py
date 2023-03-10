import pytest
from tortoise import Tortoise

from tests.models.orms.tortoise import models


@pytest.fixture(scope="module")
async def tortoise_connection():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["tests.models.orms.tortoise.models"]})
    await Tortoise.generate_schemas()
    yield Tortoise.get_connection("default")
    await Tortoise.close_connections()


@pytest.fixture
async def tortoise_superuser(tortoise_connection):
    obj = await models.TortoiseUser.create(username="Test SuperUser", password="password", is_superuser=True)
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoise_user(tortoise_connection):
    obj = await models.TortoiseUser.create(username="Test User", password="password")
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoise_tournament(tortoise_connection):
    obj = await models.TortoiseTournament.create(name="Test Tournament")
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoise_base_event(tortoise_connection):
    obj = await models.TortoiseBaseEvent.create()
    yield obj
    await obj.delete()


@pytest.fixture
async def tortoise_event(tortoise_base_event, tortoise_tournament, tortoise_user):
    obj = await models.TortoiseEvent.create(base=tortoise_base_event, name="Test Event", tournament=tortoise_tournament)
    await obj.participants.add(tortoise_user)
    yield obj
    await obj.participants.clear()
    await obj.delete()
