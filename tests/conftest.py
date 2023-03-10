import asyncio

import pytest

from tests.api.fixtures import *
from tests.models.fixtures import *


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()
