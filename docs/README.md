## Admin Dashboard App for FastAPI/Flask/Django

[![Build Status](https://github.com/vsdudakov/fastadmin/workflows/CI/badge.svg?branch=main)](https://github.com/vsdudakov/fastadmin/workflows/CI/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/vsdudakov/fastadmin/branch/main/graph/badge.svg?token=RNGX5HOW3T)](https://codecov.io/gh/vsdudakov/fastadmin)
[![License](https://img.shields.io/github/license/vsdudakov/fastadmin)](https://github.com/vsdudakov/fastadmin/blob/master/LICENSE)
[![PyPi](https://badgen.net/pypi/v/fastadmin)](https://pypi.org/project/fastadmin/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

## Screenshots

![SignIn View](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/assets/images/signin.png)
![List View](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/assets/images/list.png)
![Change View](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/assets/images/change.png)

<p align="center">
  <a href="https://twitter.com/intent/tweet?text=Admin%20Dashboard%20For%20FastAPI&url=https://github.com/vsdudakov/fastadmin&hashtags=FastAPI,AdminDashboard">
    <img alt="tweet" src="https://img.shields.io/twitter/url/https/twitter?label=Share%20on%20twitter&style=social" target="_blank" />
  </a>
</p>




## Introduction



<a href='https://github.com/vsdudakov/fastadmin' target='_blank'>FastAdmin</a> is an easy-to-use Admin Dashboard App for FastAPI/Django/Flask inspired by Django Admin.















FastAdmin was built with relations in mind and admiration for the excellent and popular Django Admin. It's engraved in its design that you may configure your admin dashboard for FastAPI/Django/Flask easiest way.















FastAdmin is designed to be minimalistic, functional and yet familiar.




















## Getting Started







If you have any questions that are beyond the scope of the documentation, Please feel free to email <a href='mailto:vsdudakov@gmail.com' target='_blank'>us</a>.













### Installation





Follow the steps below to setup FastAdmin:













Install the package using pip:



















Note: For zsh and macos use: <code>pip install fastadmin\[fastapi,django\]</code>



















```bash

pip install fastadmin[fastapi,django]  # for fastapi with django orm
pip install fastadmin[fastapi,tortoise-orm]  # for fastapi with tortoise orm
pip install fastadmin[fastapi,pony]  # for fastapi with pony orm
pip install fastadmin[fastapi,sqlalchemy]  # for fastapi with sqlalchemy orm
pip install fastadmin[django]  # for django with django orm
pip install fastadmin[django,pony]  # for django with pony orm
pip install fastadmin[flask,sqlalchemy]  # for flask with sqlalchemy

```







Install the package using poetry:























```bash

poetry add 'fastadmin[fastapi,django]'  # for fastapi with django orm
poetry add 'fastadmin[fastapi,tortoise-orm]'  # for fastapi with tortoise orm
poetry add 'fastadmin[fastapi,pony]'  # for fastapi with pony orm
poetry add 'fastadmin[fastapi,sqlalchemy]'  # for fastapi with sqlalchemy orm
poetry add 'fastadmin[django]'  # for django with django orm
poetry add 'fastadmin[django,pony]'  # for django with pony orm
poetry add 'fastadmin[flask,sqlalchemy]'  # for flask with sqlalchemy

```







Configure required settings using virtual environment variables:



















Note: You can add these variables to .env and use python-dotenv to load them. See all settings <a href='#settings'>here</a>



















```bash

export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key

```








### Quick Tutorial





Setup FastAdmin for a framework


























### FastAPI












<pre>
  <code class="language-python">
from fastapi import FastAPI

from fastadmin import fastapi_app as admin_app
from fastadmin.settings import settings


app = FastAPI()
app.mount(f"/{settings.ADMIN_PREFIX}", admin_app)

  </code>
</pre>





### Django












<pre>
  <code class="language-python">
from django.urls import path

from fastadmin import get_django_admin_urls as get_admin_urls
from fastadmin.settings import settings

urlpatterns = [
    path(f"{settings.ADMIN_PREFIX}/", get_admin_urls()),
]

  </code>
</pre>





### Flask












<pre>
  <code class="language-python">
from flask import Flask

from fastadmin import flask_app as admin_app
from fastadmin.api.frameworks.flask.app import JSONProvider
from fastadmin.settings import settings

app = Flask(__name__)
# TODO: works only here not on blueprint
app.json = JSONProvider(app)
app.register_blueprint(admin_app, url_prefix=f"/{settings.ADMIN_PREFIX}")

  </code>
</pre>










Register ORM models


























### Tortoise ORM












<pre>
  <code class="language-python">
from enum import Enum

from tortoise import fields
from tortoise.models import Model

from fastadmin import TortoiseInlineModelAdmin, TortoiseModelAdmin, action, display, register


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @classmethod
    def get_model_name(cls):
        return f"tortoiseorm.{cls.__name__}"

    class Meta:
        abstract = True


class User(BaseModel):
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)

    async def __str__(self):
        return self.username

    class Meta:
        table = "user"


class Tournament(BaseModel):
    name = fields.CharField(max_length=255)

    async def __str__(self):
        return self.name

    class Meta:
        table = "tournament"


class BaseEvent(BaseModel):
    class Meta:
        table = "base_event"


class Event(BaseModel):
    base = fields.OneToOneField("models.BaseEvent", related_name="event", null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=255)

    tournament = fields.ForeignKeyField("models.Tournament", related_name="events", on_delete=fields.CASCADE)
    participants = fields.ManyToManyField("models.User", related_name="events", through="event_participants")

    rating = fields.IntField(default=0)
    description = fields.TextField(null=True)
    event_type = fields.CharEnumField(EventTypeEnum, max_length=255, default=EventTypeEnum.PUBLIC)
    is_active = fields.BooleanField(default=True)
    start_time = fields.TimeField(null=True)
    date = fields.DateField(null=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

    json = fields.JSONField(null=True)

    async def __str__(self):
        return self.name

    class Meta:
        table = "event"


@register(User)
class TortoiseORMUserModelAdmin(TortoiseModelAdmin):
    model_name_prefix = "tortoiseorm"

    async def authenticate(self, username, password):
        obj = await self.model_cls.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id

    async def change_password(self, user_id, password):
        user = await self.model_cls.filter(id=user_id).first()
        if not user:
            return
        # direct saving password is only for tests - use hash
        user.password = password
        await user.save()


class TortoiseORMEventInlineModelAdmin(TortoiseInlineModelAdmin):
    model = Event
    model_name_prefix = "tortoiseorm"


@register(Tournament)
class TortoiseORMTournamentModelAdmin(TortoiseModelAdmin):
    inlines = (TortoiseORMEventInlineModelAdmin,)
    model_name_prefix = "tortoiseorm"


@register(BaseEvent)
class TortoiseORMBaseEventModelAdmin(TortoiseModelAdmin):
    model_name_prefix = "tortoiseorm"


@register(Event)
class TortoiseORMEventModelAdmin(TortoiseModelAdmin):
    model_name_prefix = "tortoiseorm"

    @action(description="Make user active")
    async def make_is_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=True)

    @action
    async def make_is_not_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=False)

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"

  </code>
</pre>





### Django ORM












<pre>
  <code class="language-python">
from django.db import models

from fastadmin import DjangoInlineModelAdmin, DjangoModelAdmin, action, display, register

EventTypeEnum = (
    ("PRIVATE", "PRIVATE"),
    ("PUBLIC", "PUBLIC"),
)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_model_name(cls):
        return f"django.{cls.__name__}"

    class Meta:
        abstract = True


class User(BaseModel):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"


class Tournament(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tournament"


class BaseEvent(BaseModel):
    class Meta:
        db_table = "base_event"


class Event(BaseModel):
    base = models.OneToOneField(BaseEvent, related_name="event", null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)

    tournament = models.ForeignKey(Tournament, related_name="events", on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name="events")

    rating = models.IntegerField(default=0)
    description = models.TextField(null=True)
    event_type = models.CharField(max_length=255, default="PUBLIC", choices=EventTypeEnum)
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField(null=True)
    date = models.DateField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    json = models.JSONField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "event"


@register(User)
class DjangoUserModelAdmin(DjangoModelAdmin):
    model_name_prefix = "django"

    def authenticate(self, username, password):
        obj = self.model_cls.objects.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id

    def change_password(self, user_id, password):
        user = self.model_cls.objects.filter(id=user_id).first()
        if not user:
            return
        # direct saving password is only for tests - use hash
        user.password = password
        user.save()


class DjangoEventInlineModelAdmin(DjangoInlineModelAdmin):
    model = Event
    model_name_prefix = "django"


@register(Tournament)
class DjangoTournamentModelAdmin(DjangoModelAdmin):
    model_name_prefix = "django"
    inlines = (DjangoEventInlineModelAdmin,)


@register(BaseEvent)
class DjangoBaseEventModelAdmin(DjangoModelAdmin):
    model_name_prefix = "django"


@register(Event)
class DjangoEventModelAdmin(DjangoModelAdmin):
    model_name_prefix = "django"

    @action(description="Make user active")
    def make_is_active(self, ids):
        self.model_cls.objects.filter(id__in=ids).update(is_active=True)

    @action
    def make_is_not_active(self, ids):
        self.model_cls.objects.filter(id__in=ids).update(is_active=False)

    @display
    def started(self, obj):
        return bool(obj.start_time)

    @display()
    def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"

  </code>
</pre>





### SQL Alchemy












<pre>
  <code class="language-python">
import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Time,
    select,
    update,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from fastadmin import SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin, action, display, register


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    @classmethod
    def get_model_name(cls):
        return f"sqlalchemy.{cls.__name__}"


user_m2m_event = Table(
    "event_participants",
    Base.metadata,
    Column("event_id", ForeignKey("event.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True),
)


class User(BaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(length=255), nullable=False)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    events: Mapped[List["Event"]] = relationship(secondary=user_m2m_event, back_populates="participants")

    async def __str__(self):
        return self.username


class Tournament(BaseModel):
    __tablename__ = "tournament"

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    events: Mapped[List["Event"]] = relationship(back_populates="tournament")

    async def __str__(self):
        return self.name


class BaseEvent(BaseModel):
    __tablename__ = "base_event"

    event: Mapped[Optional["Event"]] = relationship(back_populates="base")


class Event(BaseModel):
    __tablename__ = "event"

    base_id: Mapped[Optional[int]] = mapped_column(ForeignKey("base_event.id"), nullable=True)
    base: Mapped[Optional["BaseEvent"]] = relationship(back_populates="event")

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    tournament_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tournament.id"), nullable=False)
    tournament: Mapped[Optional["Tournament"]] = relationship(back_populates="events")

    participants: Mapped[list["User"]] = relationship(secondary=user_m2m_event, back_populates="events")

    rating: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=False)
    event_type: Mapped[EventTypeEnum] = mapped_column(default=EventTypeEnum.PUBLIC)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_time: Mapped[Optional[datetime.time]] = mapped_column(Time, nullable=True)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price: Mapped[Optional[Decimal]] = mapped_column(
        Float(asdecimal=True), nullable=True
    )  # max_digits=10, decimal_places=2

    json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    async def __str__(self):
        return self.name


# NOTE: provide sqlalchemy_sessionmaker as second parameter for your usage
# @register(User, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
@register(User)
class SqlAlchemyUserModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"

    async def authenticate(self, username, password):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = select(self.model_cls).filter_by(username=username, password=password, is_superuser=True)
            result = await session.scalars(query)
            obj = result.first()
            if not obj:
                return None
            return obj.id

    async def change_password(self, user_id, password):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            # direct saving password is only for tests - use hash
            query = update(self.model_cls).where(User.id.in_([user_id])).values(password=password)
            await session.execute(query)
            await session.commit()


class SqlAlchemyEventInlineModelAdmin(SqlAlchemyInlineModelAdmin):
    model_name_prefix = "sqlalchemy"

    model = Event


# NOTE: provide sqlalchemy_sessionmaker as second parameter for your usage
# @register(Tournament, sqlalchemy_sessionmaker)
@register(Tournament)
class SqlAlchemyTournamentModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"

    inlines = (SqlAlchemyEventInlineModelAdmin,)


# NOTE: provide sqlalchemy_sessionmaker as second parameter for your usage
# @register(BaseEvent, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
@register(BaseEvent)
class SqlAlchemyBaseEventModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"


# NOTE: provide sqlalchemy_sessionmaker as second parameter for your usage
# @register(Event, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
@register(Event)
class SqlAlchemyEventModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"

    @action(description="Make user active")
    async def make_is_active(self, ids):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = update(Event).where(Event.id.in_(ids)).values(is_active=True)
            await session.execute(query)
            await session.commit()

    @action
    async def make_is_not_active(self, ids):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = update(Event).where(Event.id.in_(ids)).values(is_active=False)
            await session.execute(query)
            await session.commit()

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"

  </code>
</pre>





### Pony ORM












<pre>
  <code class="language-python">
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum

from pony.orm import Database, Json, LongStr, Optional, PrimaryKey, Required, Set, commit, db_session
from pony.orm.dbapiprovider import StrConverter

from fastadmin import PonyORMInlineModelAdmin, PonyORMModelAdmin, action, display, register

db = Database()


class EnumConverter(StrConverter):
    def validate(self, val):
        if not isinstance(val, Enum):
            raise ValueError("Must be an Enum. Got {}".format(type(val)))
        return val

    def py2sql(self, val):
        return val.name

    def sql2py(self, value):
        return self.py_type[value]


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel:
    @classmethod
    def get_model_name(cls):
        return f"ponyorm.{cls.__name__}"


class User(BaseModel, db.Entity):
    _table_ = "user"

    id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow, hidden=True)
    updated_at = Required(datetime, default=datetime.utcnow, hidden=True)

    username = Required(str)
    password = Required(str)
    is_superuser = Required(bool, default=False)

    events = Set("Event", table="event_participants", column="event_id")

    def __str__(self):
        return self.username


class Tournament(BaseModel, db.Entity):
    _table_ = "tournament"

    id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow, hidden=True)
    updated_at = Required(datetime, default=datetime.utcnow, hidden=True)

    name = Required(str)

    events = Set("Event")

    def __str__(self):
        return self.name


class BaseEvent(BaseModel, db.Entity):
    _table_ = "base_event"
    id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow, hidden=True)
    updated_at = Required(datetime, default=datetime.utcnow, hidden=True)

    event = Optional("Event")


class Event(BaseModel, db.Entity):
    _table_ = "event"

    id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow, hidden=True)
    updated_at = Required(datetime, default=datetime.utcnow, hidden=True)

    base = Optional(BaseEvent, column="base_id")
    name = Required(str)

    tournament = Required(Tournament, column="tournament_id")
    participants = Set(User, table="event_participants", column="user_id")

    rating = Required(int, default=0)
    description = Optional(LongStr)
    event_type = Required(EventTypeEnum, default=EventTypeEnum.PUBLIC)
    is_active = Required(bool, default=True)
    start_time = Optional(time)
    date = Optional(date)
    latitude = Optional(float)
    longitude = Optional(float)
    price = Optional(Decimal)

    json = Optional(Json)

    def __str__(self):
        return self.name


@register(User)
class PonyORMUserModelAdmin(PonyORMModelAdmin):
    model_name_prefix = "ponyorm"

    @db_session
    def authenticate(self, username, password):
        obj = next((f for f in self.model_cls.select(username=username, password=password, is_superuser=True)), None)
        if not obj:
            return None
        return obj.id

    @db_session
    def change_password(self, user_id, password):
        obj = next((f for f in self.model_cls.select(id=user_id)), None)
        if not obj:
            return None
        # direct saving password is only for tests - use hash
        obj.password = password
        commit()


class PonyORMEventInlineModelAdmin(PonyORMInlineModelAdmin):
    model = Event
    model_name_prefix = "ponyorm"


@register(Tournament)
class PonyORMTournamentModelAdmin(PonyORMModelAdmin):
    inlines = (PonyORMEventInlineModelAdmin,)
    model_name_prefix = "ponyorm"


@register(BaseEvent)
class PonyORMBaseEventModelAdmin(PonyORMModelAdmin):
    model_name_prefix = "ponyorm"


@register(Event)
class PonyORMEventModelAdmin(PonyORMModelAdmin):
    model_name_prefix = "ponyorm"

    @action(description="Make user active")
    @db_session
    def make_is_active(self, ids):
        # update(o.set(is_active=True) for o in self.model_cls if o.id in ids)
        objs = self.model_cls.select(lambda o: o.id in ids)
        for obj in objs:
            obj.is_active = True
        commit()

    @action
    @db_session
    def make_is_not_active(self, ids):
        # update(o.set(is_active=False) for o in self.model_cls if o.id in ids)
        objs = self.model_cls.select(lambda o: o.id in ids)
        for obj in objs:
            obj.is_active = False
        commit()

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"

  </code>
</pre>
























## Documentation

See full documentation [here](https://vsdudakov.github.io/fastadmin).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsdudakov/fastadmin/blob/main/LICENSE) file for details.
