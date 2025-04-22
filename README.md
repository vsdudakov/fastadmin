## Admin Dashboard App for FastAPI/Flask/Django

[![codecov](https://codecov.io/gh/vsdudakov/fastadmin/branch/main/graph/badge.svg?token=RNGX5HOW3T)](https://codecov.io/gh/vsdudakov/fastadmin)
[![License](https://img.shields.io/github/license/vsdudakov/fastadmin)](https://github.com/vsdudakov/fastadmin/blob/master/LICENSE)
[![PyPi](https://badgen.net/pypi/v/fastadmin)](https://pypi.org/project/fastadmin/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

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














  




Note: For zsh and macos use: <code>pip install fastadmin[fastapi,django]</code>










  








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














  




Note: You can add these variables to .env and use python-dotenv to load them. See all settings <a href='https://vsdudakov.github.io/fastadmin#settings'>here</a>










  








```bash

export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key

```







### Quick Tutorial

  


Setup FastAdmin for a framework












  













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
import typing as tp
from uuid import UUID

import bcrypt
from tortoise import fields
from tortoise.models import Model

from fastadmin import TortoiseModelAdmin, WidgetType, register


class User(Model):
    username = fields.CharField(max_length=255, unique=True)
    hash_password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=False)
    avatar_url = fields.TextField(null=True)

    def __str__(self):
        return self.username


@register(User)
class UserAdmin(TortoiseModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
        "avatar_url": (
            WidgetType.Upload,
            {
                "required": False,
                # Disable crop image for upload field
                # "disableCropImage": True,
            },
        ),
    }

    async def authenticate(self, username: str, password: str) -> int | None:
        user = await self.model_cls.filter(phone=username, is_superuser=True).first()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return None
        return user.id

    async def change_password(self, id: UUID | int, password: str) -> None:
        user = await self.model_cls.filter(id=id).first()
        if not user:
            return
        user.hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        await user.save(update_fields=("hash_password",))

    async def orm_save_upload_field(self, obj: tp.Any, field: str, base64: str) -> None:
        # convert base64 to bytes, upload to s3/filestorage, get url and save or save base64 as is to db (don't recomment it)
        setattr(obj, field, base64)
        await obj.save(update_fields=(field,))

```






### Django ORM












```python
from django.db import models

from fastadmin import DjangoModelAdmin, register


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    hash_password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.username


@register(User)
class UserAdmin(DjangoModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    def authenticate(self, username, password):
        obj = User.objects.filter(username=username, is_superuser=True).first()
        if not obj:
            return None
        if not obj.check_password(password):
            return None
        return obj.id

```






### SQL Alchemy












```python
import typing as tp
import uuid

import bcrypt
from sqlalchemy import Boolean, Integer, String, Text, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from fastadmin import SqlAlchemyModelAdmin, register

sqlalchemy_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=True,
)
sqlalchemy_sessionmaker = async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(String(length=255), nullable=False)
    hash_password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __str__(self):
        return self.username


@register(User, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class UserAdmin(SqlAlchemyModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    async def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = select(self.model_cls).filter_by(username=username, password=password, is_superuser=True)
            result = await session.scalars(query)
            obj = result.first()
            if not obj:
                return None
            if not bcrypt.checkpw(password.encode(), obj.hash_password.encode()):
                return None
            return obj.id

    async def change_password(self, id: uuid.UUID | int, password: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            query = update(self.model_cls).where(User.id.in_([id])).values(hash_password=hash_password)
            await session.execute(query)
            await session.commit()

    async def orm_save_upload_field(self, obj: tp.Any, field: str, base64: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            # convert base64 to bytes, upload to s3/filestorage, get url and save or save base64 as is to db (don't recomment it)
            query = update(self.model_cls).where(User.id.in_([obj.id])).values(**{field: base64})
            await session.execute(query)
            await session.commit()

```






### Pony ORM












```python
import typing as tp
import uuid

import bcrypt
from pony.orm import Database, LongStr, Optional, PrimaryKey, Required, commit, db_session

from fastadmin import PonyORMModelAdmin, register

db = Database()
db.bind(provider="sqlite", filename=":memory:", create_db=True)


class User(db.Entity):  # type: ignore [name-defined]
    _table_ = "user"
    id = PrimaryKey(int, auto=True)
    username = Required(str)
    hash_password = Required(str)
    is_superuser = Required(bool, default=False)
    is_active = Required(bool, default=False)
    avatar_url = Optional(LongStr, nullable=True)

    def __str__(self):
        return self.username


@register(User)
class UserAdmin(PonyORMModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    @db_session
    def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        obj = next((f for f in User.select(username=username, password=password, is_superuser=True)), None)  # fmt: skip
        if not obj:
            return None
        if not bcrypt.checkpw(password.encode(), obj.hash_password.encode()):
            return None
        return obj.id

    @db_session
    def change_password(self, id: uuid.UUID | int, password: str) -> None:
        obj = next((f for f in self.model_cls.select(id=id)), None)
        if not obj:
            return
        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        obj.hash_password = hash_password
        commit()

    @db_session
    def orm_save_upload_field(self, obj: tp.Any, field: str, base64: str) -> None:
        obj = next((f for f in self.model_cls.select(id=obj.id)), None)
        if not obj:
            return
        # convert base64 to bytes, upload to s3/filestorage, get url and save or save base64 as is to db (don't recomment it)
        setattr(obj, field, base64)
        commit()

```






















## Documentation
See full documentation [here](https://vsdudakov.github.io/fastadmin).

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsdudakov/fastadmin/blob/main/LICENSE) file for details.