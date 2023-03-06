## Admin Dashboard App for FastAPI

[![Build Status](https://github.com/vsdudakov/fastadmin/workflows/CI/badge.svg?branch=main)](https://github.com/vsdudakov/fastadmin/workflows/CI/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/vsdudakov/fastadmin/branch/main/graph/badge.svg?token=RNGX5HOW3T)](https://codecov.io/gh/vsdudakov/fastadmin)
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

```bash
pip install fastadmin
```

or using poetry

```bash
poetry install fastadmin
```

### Quick Tutorial

#### Mount FastAdmin app

First of all you need to mount FastAdmin app into your app.
Use prefix "/admin" as default for now. You can change it later.

Example:

```python
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

```bash
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

```python
import bcrypt
from tortoise.models import Model
from fastadmin import TortoiseModelAdmin, register


class User(Model):
    username = fields.CharField(max_length=255, unique=True)
    hash_password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=False)

    ...



class Group(Model):
    name = fields.CharField(max_length=255)
    ...


@register(User)
class UserAdmin(TortoiseModelAdmin):
    async def authenticate(self, username: str, password: str) -> UUID | int | None:
        user = await User.filter(username=username, is_superuser=True).first()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return None
        return user.id


@register(Group)
class GroupAdmin(TortoiseModelAdmin):
    pass
```

#### Run your project

Run your project (see [https://fastapi.tiangolo.com/tutorial/first-steps/](https://fastapi.tiangolo.com/tutorial/first-steps/)):

```bash
uvicorn ...
```

Go to [http://localhost:8000/admin](http://localhost:8000/admin).

## Documentation

See full documentation [here](https://vsdudakov.github.io/fastadmin/).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsdudakov/fastadmin/blob/main/LICENSE) file for details.
