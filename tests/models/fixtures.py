from copy import copy

import pytest

from fastadmin.models.base import admin_models as admin_models_objs
from tests.models.orms.tortoise.fixtures import *

orms = ["tortoise"]


@pytest.fixture(params=orms)
async def superuser(request, tortoise_superuser):
    match request.param:
        case "tortoise":
            yield tortoise_superuser


@pytest.fixture(params=orms)
async def user(request, tortoise_user):
    match request.param:
        case "tortoise":
            yield tortoise_user


@pytest.fixture(params=orms)
async def tournament(request, tortoise_tournament):
    match request.param:
        case "tortoise":
            yield tortoise_tournament


@pytest.fixture(params=orms)
async def base_event(request, tortoise_base_event):
    match request.param:
        case "tortoise":
            yield tortoise_base_event


@pytest.fixture(params=orms)
async def event(request, tortoise_event):
    match request.param:
        case "tortoise":
            yield tortoise_event


@pytest.fixture
async def admin_models():
    prev_admin_models = {k: copy(v) for k, v in admin_models_objs.items()}
    yield admin_models_objs
    for k, v in prev_admin_models.items():
        admin_models_objs[k] = v
