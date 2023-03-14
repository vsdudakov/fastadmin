from copy import copy

import pytest

from fastadmin.models.base import admin_models as admin_models_objs
from tests.models.orms.django.fixtures import *
from tests.models.orms.sqlalchemy.fixtures import *
from tests.models.orms.tortoise.fixtures import *

orms = [
    "tortoise",
    "djangoorm",
    "sqlalchemy",
]


@pytest.fixture(params=orms)
async def superuser(request, tortoise_superuser, django_superuser, sqlalchemy_superuser):
    match request.param:
        case "tortoise":
            yield tortoise_superuser
        case "djangoorm":
            yield django_superuser
        case "sqlalchemy":
            yield sqlalchemy_superuser


@pytest.fixture(params=orms)
async def user(request, tortoise_user, django_user, sqlalchemy_user):
    match request.param:
        case "tortoise":
            yield tortoise_user
        case "djangoorm":
            yield django_user
        case "sqlalchemy":
            yield sqlalchemy_user


@pytest.fixture(params=orms)
async def tournament(request, tortoise_tournament, django_tournament, sqlalchemy_tournament):
    match request.param:
        case "tortoise":
            yield tortoise_tournament
        case "djangoorm":
            yield django_tournament
        case "sqlalchemy":
            yield sqlalchemy_tournament


@pytest.fixture(params=orms)
async def base_event(request, tortoise_base_event, django_base_event, sqlalchemy_base_event):
    match request.param:
        case "tortoise":
            yield tortoise_base_event
        case "djangoorm":
            yield django_base_event
        case "sqlalchemy":
            yield sqlalchemy_base_event


@pytest.fixture(params=orms)
async def event(request, tortoise_event, django_event, sqlalchemy_event):
    match request.param:
        case "tortoise":
            yield tortoise_event
        case "djangoorm":
            yield django_event
        case "sqlalchemy":
            yield sqlalchemy_event


@pytest.fixture
async def admin_models():
    prev_admin_models = {k: copy(v) for k, v in admin_models_objs.items()}
    yield admin_models_objs
    for k, v in prev_admin_models.items():
        admin_models_objs[k] = v
