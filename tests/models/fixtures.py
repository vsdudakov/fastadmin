from copy import copy

import pytest

from fastadmin.models.base import admin_models as admin_models_objs
from tests.models.orms.django.fixtures import *
from tests.models.orms.ponyorm.fixtures import *
from tests.models.orms.sqlalchemy.fixtures import *
from tests.models.orms.tortoiseorm.fixtures import *
from tests.settings import ORMS


@pytest.fixture(params=ORMS)
async def superuser(request, tortoiseorm_superuser, django_superuser, sqlalchemy_superuser, ponyorm_superuser):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_superuser
        case "djangoorm":
            yield django_superuser
        case "sqlalchemy":
            yield sqlalchemy_superuser
        case "ponyorm":
            yield ponyorm_superuser


@pytest.fixture(params=ORMS)
async def user(request, tortoiseorm_user, django_user, sqlalchemy_user, ponyorm_user):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_user
        case "djangoorm":
            yield django_user
        case "sqlalchemy":
            yield sqlalchemy_user
        case "ponyorm":
            yield ponyorm_user


@pytest.fixture(params=ORMS)
async def tournament(request, tortoiseorm_tournament, django_tournament, sqlalchemy_tournament, ponyorm_tournament):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_tournament
        case "djangoorm":
            yield django_tournament
        case "sqlalchemy":
            yield sqlalchemy_tournament
        case "ponyorm":
            yield ponyorm_tournament


@pytest.fixture(params=ORMS)
async def base_event(request, tortoiseorm_base_event, django_base_event, sqlalchemy_base_event, ponyorm_base_event):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_base_event
        case "djangoorm":
            yield django_base_event
        case "sqlalchemy":
            yield sqlalchemy_base_event
        case "ponyorm":
            yield ponyorm_base_event


@pytest.fixture(params=ORMS)
async def event(request, tortoiseorm_event, django_event, sqlalchemy_event, ponyorm_event):
    match request.param:
        case "tortoiseorm":
            yield tortoiseorm_event
        case "djangoorm":
            yield django_event
        case "sqlalchemy":
            yield sqlalchemy_event
        case "ponyorm":
            yield ponyorm_event


@pytest.fixture
async def admin_models():
    prev_admin_models = {k: copy(v) for k, v in admin_models_objs.items()}
    yield admin_models_objs
    for k, v in prev_admin_models.items():
        admin_models_objs[k] = v
