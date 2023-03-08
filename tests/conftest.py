import asyncio

import pytest


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


from tests.api.fastapi.fixtures import *  # noqa: F401, F403
from tests.models.orms.tortoise.fixtures import *  # noqa: F401, F403
