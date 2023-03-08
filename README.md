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

FastAdmin is an easy-to-use Admin App for FastAPI inspired by Django Admin.

FastAdmin was built with relations in mind and admiration for the excellent and popular Django Admin.
It's engraved in its design that you may configure your admin dashboard for FastAPI/Flask/Django easiest way.

FastAdmin is designed to be minimalistic, functional and yet familiar.

## Getting Started

### Installation

#### Install the package using pip:

```bash
pip install fastadmin
```

#### Setup ENV variables

```bash
export ADMIN_USER_MODEL = User
export ADMIN_USER_MODEL_USERNAME_FIELD = username
export ADMIN_SECRET_KEY = secret_key
```

For additional information see [Settings](https://vsdudakov.github.io/fastadmin#settings) documentation.

### Quick Tutorial

#### Setup FastAdmin for framework

##### For FastAPI:

```python
from fastapi import FastAPI
from fastadmin import fastapi_app as admin_app

...

app = FastAPI()

...

app.mount("/admin", admin_app)

...
```

Run your project (see [https://fastapi.tiangolo.com/tutorial/first-steps/](https://fastapi.tiangolo.com/tutorial/first-steps/)):

```bash
uvicorn ...
```

Go to [http://localhost:8000/admin](http://localhost:8000/admin).

For additional information see [ModelAdmin](https://vsdudakov.github.io/fastadmin#model_admin_objects) and [InlineModelAdmin](https://vsdudakov.github.io/fastadmin#inline_model_admin_objects) documentation.

##### For Django and Flask:

Coming soon...

#### Register ORM models

You have to implement authenticate method for FastAdmin authentication on AdminModel class which is registered for ADMIN_USER_MODEL.

##### For Tortoise ORM:

```python
import bcrypt
from tortoise.models import Model
from fastadmin import register, TortoiseModelAdmin


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
    label_fields = ("username",)
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    async def authenticate(self, username: str, password: str) -> UUID | int | None:
        user = await User.filter(username=username, is_superuser=True).first()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return None
        return user.id


@register(Group)
class GroupAdmin(TortoiseModelAdmin):
    label_fields = ("name",)
    list_display = ("id", "name")
    list_display_links = ("id",)
    list_filter = ("id", "name")
    search_fields = ("name",)
```

##### For SQLAlchemy and PonyORM:

Coming soon...

## Documentation

See full documentation [here](https://vsdudakov.github.io/fastadmin).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/vsdudakov/fastadmin/blob/main/LICENSE) file for details.
