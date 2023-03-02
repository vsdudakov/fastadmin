## Admin Dashboard App for FastAPI

[![Build Status](https://github.com/vsdudakov/fastadmin/workflows/CI/badge.svg?branch=main)](https://github.com/vsdudakov/fastadmin/workflows/CI/badge.svg?branch=main)
[![Coverage](https://badgen.net/codecov/c/github/vsdudakov/fastadmin)](https://app.codecov.io/gh/vsdudakov/fastadmin)
[![License](https://img.shields.io/github/license/vsdudakov/fastadmin)](https://github.com/vsdudakov/fastadmin/blob/master/LICENSE)
[![PyPi](https://badgen.net/pypi/v/fastadmin)](https://pypi.org/project/fastadmin/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

## Screenshots

![SignIn View](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/images/signin.png)
![List View](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/images/list.png)
![Change View](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/images/change.png)

## Introduction

FastAdmin is an easy-to-use Admin App for FastAPI inspired by Django Admin.

FastAdmin was built with relations in mind and admiration for the excellent and popular Django Admin. It's engraved in its design that you may configure your admin dashboard for FastAPI easiest way.

Note

FastAdmin supports only Tortoise ORM (SQLAlchemy, Pony ORM and others are in plans).

## Why was FastAdmin built?

FastAPI is gaining huge popularity as an asyncio, minimalistic API framework, but there is no simple and clear system for administration your data.

Hence we started FastAdmin.

FastAdmin is designed to be minimalistic, functional, yet familiar, to ease the migration of developers wishing to switch to FastAPI from Django.

## Getting Started

### Installation

First you have to install FastAdmin like this:

```
pip install fastadmin
```

or using poetry

```
poetry install fastadmin
```

### Quick Tutorial

#### Mount FastAdmin app

First of all you need to mount FastAdmin app into your app.
Use prefix "/admin" as default for now. You can change it later.

Example:

```
from fastapi import FastAPI
from fastadmin import admin_app

...

app = FastAPI()

...

app.mount("/admin", admin_app)

...
```

#### Setup ENV variables

Setup the following env variables to configure FastAdmin (add to .env or export them like on example):

Example:

```
export ADMIN_USER_MODEL = User
export ADMIN_USER_MODEL_USERNAME_FIELD = username
export ADMIN_SECRET_KEY = secret_key
```

- ADMIN_USER_MODEL - a name of your User model (has to be registered in FastAdmin later)
- ADMIN_USER_MODEL_USERNAME_FIELD - an username field (unique field from your user table) for authentication (could be email, or phone)
- ADMIN_SECRET_KEY - a secret key (generate a strong secret key and provide here)

#### Register ORM models

Implement an authenticate method for ModelAdmin with registered model ADMIN_USER_MODEL

Example (for Tortoise ORM):

```
import bcrypt
from tortoise.models import Model
from fastadmin import TortoiseModelAdmin, register


class User(Model):
    username = fields.CharField(max_length=255, unique=True)
    hash_password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)

    ...



class Group(Model):
    name = fields.CharField(max_length=255)
    ...


@register(User)
class UserAdmin(TortoiseModelAdmin):
    async def authenticate(self, username: str, password: str) -> User | None:
        user = await User.filter(username=username, is_superuser=True).first()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return None
        return user


@register(Group)
class GroupAdmin(TortoiseModelAdmin):
    pass
```

#### Run your project

Run your project (see https://fastapi.tiangolo.com/tutorial/first-steps/):

```
uvicorn ...
```

Go to http://localhost:8000/admin

## Configuration

You can find all env variables to configure FastAdmin [here](https://github.com/vsdudakov/fastadmin/blob/main/fastadmin/settings.py)

You can find all parameters and methods to configure your ModelAdmin classes [here](https://github.com/vsdudakov/fastadmin/blob/main/fastadmin/models/base.py)

Example:

```
@register(User)
class UserAdmin(TortoiseModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username")

    def has_delete_permission(self) -> bool:
        return False

    ...
```

## Other ORMs or own implementation

We are going to support SQLAlchemy and Pony ORM soon...

If you have smth else (your own implementation of ORM and so on) you will may overload ModelAdmin class and implement the following interfaces

```
from typing import Any
from collections import OrderedDict
from fastadmin import ModelAdmin

class MyModelAdmin(ModelAdmin):
    async def save_model(self, obj: Any, payload: dict, add: bool = False) -> None:
        """This method is used to save orm/db model object.

        :params obj: an orm/db model object.
        :params payload: a payload from request.
        :params add: a flag for add or update object.
        :return: None.
        """
        raise NotImplementedError

    async def delete_model(self, obj: Any) -> None:
        """This method is used to delete orm/db model object.

        :params obj: an orm/db model object.
        :return: None.
        """
        raise NotImplementedError

    async def get_obj(self, id: str) -> Any | None:
        """This method is used to get orm/db model object by id.

        :params id: an id of object.
        :return: An object or None.
        """
        raise NotImplementedError

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[Any], int]:
        """This method is used to get list of orm/db model objects.

        :params offset: an offset for pagination.
        :params limit: a limit for pagination.
        :params search: a search query.
        :params sort_by: a sort by field name.
        :params filters: a dict of filters.
        :return: A tuple of list of objects and total count.
        """
        raise NotImplementedError

    def get_model_fields(self) -> OrderedDict[str, dict]:
        """This method is used to get all orm/db model fields
        with saving ordering (non relations, fk, o2o, m2m).

        :return: An OrderedDict of model fields.
        """
        raise NotImplementedError

    def get_form_widget(self, field_name: str) -> tuple[WidgetType, dict]:
        """This method is used to get form item widget
        for field from orm/db model.

        :params field_name: a model field name.
        :return: A tuple of widget type and widget props.
        """
        raise NotImplementedError

```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsdudakov/fastadmin/blob/main/LICENSE) file for details.
