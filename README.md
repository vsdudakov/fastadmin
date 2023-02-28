## Admin App for FastAPI

[![Build Status](https://github.com/vsdudakov/fastadmin/workflows/CI/badge.svg?branch=main)](https://github.com/vsdudakov/fastadmin/workflows/CI/badge.svg?branch=main)
[![Coverage](https://badgen.net/codecov/c/github/vsdudakov/fastadmin)](https://app.codecov.io/gh/vsdudakov/fastadmin)
[![License](https://img.shields.io/github/license/vsdudakov/fastadmin)](https://github.com/vsdudakov/fastadmin/blob/master/LICENSE)
[![PyPi](https://badgen.net/pypi/v/fastadmin)](https://pypi.org/project/fastadmin/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)


## Introduction
FastAdmin is an easy-to-use Admin App for FastAPI inspired by Django Admin.

FastAdmin was built with relations in mind and admiration for the excellent and popular Django Admin. It's engraved in its design that you may configure your admin pages easiest way.

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

#### Implement check_password method

Add check_password method to your User model (we need it for authentication):

Example for Tortoise ORM:
```
import bcrypt
from tortoise.models import Model

class User(Model):
    username = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)

    ...

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

```

#### Register your ORM models

For Tortoise ORM (we support only Tortoise ORM for now):

```
import bcrypt
from tortoise.models import Model

from fastadmin import TortoiseModelAdmin, register


class User(Model):
    username = fields.CharField(max_length=255, unique=True)
    hash_password = fields.CharField(max_length=255)

    ...

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


@register(User)
class UserAdmin(TortoiseModelAdmin):
    pass
```

#### Enjoy

Run your project (see https://fastapi.tiangolo.com/tutorial/first-steps/):
```
uvicorn ...
```

Go to http://localhost:8000/admin


## License

This project is licensed under the MIT License - see the LICENSE.txt file for details.
