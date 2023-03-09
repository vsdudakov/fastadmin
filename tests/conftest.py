import asyncio

import pytest


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


from tests.api.fixtures import *
from tests.models.fixtures import *
