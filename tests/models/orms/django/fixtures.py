import pytest

from tests.dev.djangoorm import models
from tests.dev.djangoorm.helpers import close_connection, get_connection, init_connection


@pytest.fixture(scope="session")
def django_connection():
    init_connection()
    yield get_connection()
    close_connection()


@pytest.fixture
async def django_db(django_connection):
    yield django_connection


@pytest.fixture
def django_superuser(django_db):
    obj = models.User.objects.create(username="Test SuperUser", password="password", is_superuser=True)
    yield obj
    obj.delete()


@pytest.fixture
def django_user(django_db):
    obj = models.User.objects.create(username="Test User", password="password")
    yield obj
    obj.delete()


@pytest.fixture
def django_tournament(django_db):
    obj = models.Tournament.objects.create(name="Test Tournament")
    yield obj
    obj.delete()


@pytest.fixture
def django_base_event(django_db):
    obj = models.BaseEvent.objects.create()
    yield obj
    obj.delete()


@pytest.fixture
def django_event(django_base_event, django_tournament, django_user):
    obj = models.Event.objects.create(base=django_base_event, name="Test Event", tournament=django_tournament)
    obj.participants.add(django_user)
    yield obj
    obj.delete()
