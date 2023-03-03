import asyncio
import pytest
from tortoise import Tortoise

from tests.tortoise.models import Tournament, Event, User



@pytest.fixture(scope="session", autouse=True)
async def tortoise_db():
    await Tortoise.init(
        db_url='sqlite://:memory:',
        modules={'models': ['tests.tortoise.models']}
    )
    await Tortoise.generate_schemas()
    yield Tortoise.get_connection('default')
    await Tortoise.close_connections()


@pytest.fixture
async def user():
    user = await User.create(username='Test User', password='password')
    yield user
    await user.delete()


@pytest.fixture
async def tournament():
    tournament = await Tournament.create(name='Test Tournament')
    yield tournament
    await tournament.delete()


@pytest.fixture
async def event(tournament, user):
    event = await Event.create(name='Test Event', tournament=tournament)
    await event.participants.add(user)
    yield event
    await event.delete()
