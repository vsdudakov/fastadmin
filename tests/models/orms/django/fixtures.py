import django
import pytest
from django.db import connections

from examples.djangoorm import models
from fastadmin.models.helpers import get_admin_model


@pytest.fixture(scope="session", autouse=True)
def django_session():
    django.setup(set_prefix=False)
    session = connections["default"]
    yield session


@pytest.fixture
def django_superuser():
    obj = models.User.objects.create(username="Test SuperUser", password="password", is_superuser=True)
    yield obj
    obj.delete()


@pytest.fixture
def django_user():
    obj = models.User.objects.create(username="Test User", password="password")
    yield obj
    obj.delete()


@pytest.fixture
def django_tournament():
    obj = models.Tournament.objects.create(name="Test Tournament")
    yield obj
    obj.delete()


@pytest.fixture
def django_base_event():
    obj = models.BaseEvent.objects.create()
    yield obj
    obj.delete()


@pytest.fixture
def django_event(django_base_event, django_tournament, django_user):
    obj = models.Event.objects.create(base=django_base_event, name="Test Event", tournament=django_tournament)
    obj.participants.add(django_user)
    yield obj
    obj.delete()
