# Admin Dashboard for FastAPI / Flask / Django

[![codecov](https://codecov.io/gh/vsdudakov/fastadmin/branch/main/graph/badge.svg?token=RNGX5HOW3T)](https://app.codecov.io/gh/vsdudakov/fastadmin)
[![License](https://img.shields.io/github/license/vsdudakov/fastadmin)](https://github.com/vsdudakov/fastadmin/blob/master/LICENSE)
[![PyPi](https://badgen.net/pypi/v/fastadmin)](https://pypi.org/project/fastadmin/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

## Screenshots

![Sign-in view](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/assets/images/signin.png)
![List view](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/assets/images/list.png)
![Change view](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/assets/images/change.png)

<p align="center">
  <a href="https://twitter.com/intent/tweet?text=Admin%20Dashboard%20For%20FastAPI&url=https://github.com/vsdudakov/fastadmin&hashtags=FastAPI,AdminDashboard">
    <img alt="tweet" src="https://img.shields.io/twitter/url/https/twitter?label=Share%20on%20twitter&style=social" target="_blank" />
  </a>
</p>



## Introduction

  
<a href='https://github.com/vsdudakov/fastadmin' target='_blank'>FastAdmin</a> is an easy-to-use admin dashboard for FastAPI, Django, and Flask, inspired by Django Admin.














  
FastAdmin is built with relationships in mind and admiration for Django Admin. Its design focuses on making it as easy as possible to configure your admin dashboard for FastAPI, Django, or Flask.














  
FastAdmin aims to be minimal, functional, and familiar.


















## Getting Started

  




If you have questions beyond this documentation, feel free to <a href='mailto:vsdudakov@gmail.com' target='_blank'>email us</a>.












### Installation

  


Follow the steps below to set up FastAdmin:












  
Install the package with pip:














  




On zsh and macOS, use quotes: <code>pip install 'fastadmin[fastapi,django]'</code>










  








```bash

pip install fastadmin[fastapi,django]        # FastAPI with Django ORM
pip install fastadmin[fastapi,tortoise-orm]  # FastAPI with Tortoise ORM
pip install fastadmin[fastapi,pony]          # FastAPI with Pony ORM
pip install fastadmin[fastapi,sqlalchemy]    # FastAPI with SQLAlchemy (includes greenlet)
pip install fastadmin[django]                # Django with Django ORM
pip install fastadmin[django,pony]           # Django with Pony ORM
pip install fastadmin[flask,sqlalchemy]      # Flask with SQLAlchemy (includes greenlet)

```






  
Or install with Poetry:














  








```bash

poetry add 'fastadmin[fastapi,django]'
poetry add 'fastadmin[fastapi,tortoise-orm]'
poetry add 'fastadmin[fastapi,pony]'
poetry add 'fastadmin[fastapi,sqlalchemy]'
poetry add 'fastadmin[django]'
poetry add 'fastadmin[django,pony]'
poetry add 'fastadmin[flask,sqlalchemy]'

```






  




When using SQLAlchemy, the <code>greenlet</code> package is required (included in the <code>fastadmin[sqlalchemy]</code> extra).










  
Configure the required settings with environment variables:














  




You can add these variables to a <code>.env</code> file and load them with python-dotenv. See <a href='https://vsdudakov.github.io/fastadmin#settings'>all settings</a> in the full documentation.










  








```bash

export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key

```







### Quick Tutorial

  


Set up FastAdmin for your framework












  













### FastAPI












```python
from fastapi import FastAPI

from fastadmin import fastapi_app as admin_app

app = FastAPI()

app.mount("/admin", admin_app)

```






### Django












```python
from django.urls import path

from fastadmin import get_django_admin_urls as get_admin_urls
from fastadmin.settings import settings

urlpatterns = [
    path(f"{settings.ADMIN_PREFIX}/", get_admin_urls()),
]

```






### Flask












```python
from flask import Flask

from fastadmin import flask_app as admin_app

app = Flask(__name__)

app.register_blueprint(admin_app, url_prefix="/admin")

```








  


Register ORM models












  













### Tortoise ORM












```python
from enum import Enum

from tortoise import fields
from tortoise.models import Model


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)

    avatar_url = fields.TextField(null=True)

    def __str__(self):
        return self.username

    class Meta:
        table = "user"


class UserAttachment(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="attachments", on_delete=fields.CASCADE)
    attachment_url = fields.TextField()


class Tournament(BaseModel):
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        table = "tournament"


class BaseEvent(BaseModel):
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name

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
    start_time = fields.DatetimeField(null=True)
    date = fields.DateField(null=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

    json = fields.JSONField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        table = "event"

```






### Django ORM












```python
import uuid

from django.db import models

from fastadmin import DjangoInlineModelAdmin, DjangoModelAdmin, WidgetType, action, display, register

EventTypeEnum = (
    ("PRIVATE", "PRIVATE"),
    ("PUBLIC", "PUBLIC"),
)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)

    avatar_url = models.ImageField(null=True)
    attachment_url = models.FileField()

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
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

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
class UserModelAdmin(DjangoModelAdmin):
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
    }

    def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        obj = self.model_cls.objects.filter(username=username, is_superuser=True).first()
        if not obj:
            return None
        # if not obj.check_password(password):
        #     return None
        return obj.id

    def change_password(self, id: uuid.UUID | int, password: str) -> None:
        user = self.model_cls.objects.filter(id=id).first()
        if not user:
            return
        # direct saving password is only for tests - use hash
        user.password = password
        user.save()

    def upload_file(
        self,
        field_name: str,
        file_name: str,
        file_content: bytes,
    ) -> str:
        # save file to media directory or to s3/filestorage here
        return f"/media/{file_name}"


class EventInlineModelAdmin(DjangoInlineModelAdmin):
    model = Event


@register(Tournament)
class TournamentModelAdmin(DjangoModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent)
class BaseEventModelAdmin(DjangoModelAdmin):
    pass


@register(Event)
class EventModelAdmin(DjangoModelAdmin):
    actions = ("make_is_active", "make_is_not_active")
    list_display = ("id", "tournament", "name_with_price", "rating", "event_type", "is_active", "started")
    list_filter = ("tournament", "event_type", "is_active")
    search_fields = ("name", "tournament__name")

    @action(description="Make event active")
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

```






### SQLAlchemy












```python
import datetime
import typing as tp
from decimal import Decimal
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, Text, Time
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

sqlalchemy_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
sqlalchemy_sessionmaker = async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


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

    events: Mapped[list["Event"]] = relationship(secondary=user_m2m_event, back_populates="participants")
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment_url: Mapped[str] = mapped_column(Text, nullable=False)

    def __str__(self):
        return self.username


class Tournament(BaseModel):
    __tablename__ = "tournament"

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    events: Mapped[list["Event"]] = relationship(back_populates="tournament")

    def __str__(self):
        return self.name


class BaseEvent(BaseModel):
    __tablename__ = "base_event"

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    event: Mapped[tp.Optional["Event"]] = relationship(back_populates="base")

    def __str__(self):
        return self.name


class Event(BaseModel):
    __tablename__ = "event"

    base_id: Mapped[int | None] = mapped_column(ForeignKey("base_event.id"), nullable=True)
    base: Mapped[tp.Optional["BaseEvent"]] = relationship(back_populates="event")

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    tournament_id: Mapped[int | None] = mapped_column(ForeignKey("tournament.id"), nullable=False)
    tournament: Mapped[tp.Optional["Tournament"]] = relationship(back_populates="events")

    participants: Mapped[list["User"]] = relationship(secondary=user_m2m_event, back_populates="events")

    rating: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=False)
    event_type: Mapped[EventTypeEnum] = mapped_column(default=EventTypeEnum.PUBLIC)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_time: Mapped[datetime.time | None] = mapped_column(Time, nullable=True)
    date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    price: Mapped[Decimal | None] = mapped_column(
        Float(asdecimal=True), nullable=True
    )  # max_digits=10, decimal_places=2

    json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __str__(self):
        return self.name

```






### Pony ORM












```python
from datetime import UTC, date, datetime, time
from decimal import Decimal
from enum import Enum

from pony.orm import Database, Json, LongStr, Optional, PrimaryKey, Required, Set

db = Database()


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel:
    # id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Required(datetime, default=datetime.utcnow)

    def before_update(self):
        self.updated_at = datetime.now(tz=UTC)


class User(db.Entity, BaseModel):
    _table_ = "user"

    username = Required(str, max_len=255)
    password = Required(str, max_len=255)
    is_superuser = Required(bool, default=False)

    avatar_url = Optional(LongStr, nullable=True)
    attachment_url = Required(LongStr)

    events = Set("Event", table="event_participants", column="event_id")

    def __str__(self):
        return self.username


class Tournament(db.Entity, BaseModel):
    _table_ = "tournament"

    name = Required(str, max_len=255)

    events = Set("Event")

    def __str__(self):
        return self.name


class BaseEvent(db.Entity, BaseModel):
    _table_ = "base_event"

    id = PrimaryKey(int, auto=True)
    name = Required(str, max_len=255)

    event = Optional("Event")

    def __str__(self):
        return self.name


class Event(db.Entity, BaseModel):
    _table_ = "event"

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

```






















## Documentation

Full documentation is available at [vsdudakov.github.io/fastadmin](https://vsdudakov.github.io/fastadmin).

## License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/vsdudakov/fastadmin/blob/main/LICENSE) file for details.