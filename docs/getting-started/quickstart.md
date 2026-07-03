---
title: Quick start
description: Mount the FastAdmin dashboard into FastAPI, Flask or Django and register your first model admin.
---

# Quick start

This page takes you from an installed package to a working admin dashboard.
It assumes you finished [Installation](installation.md) and exported the
required `ADMIN_*` environment variables.

## 1. Mount the admin app

=== "FastAPI"

    ```python
    from fastapi import FastAPI

    from fastadmin import fastapi_app as admin_app

    app = FastAPI()
    app.mount("/admin", admin_app)
    ```

=== "Flask"

    ```python
    from flask import Flask

    from fastadmin import flask_app as admin_app
    from fastadmin.settings import settings

    app = Flask(__name__)
    app.register_blueprint(admin_app, url_prefix=f"/{settings.ADMIN_PREFIX}")
    ```

=== "Django"

    ```python
    # urls.py
    from django.urls import path

    from fastadmin import get_django_admin_urls as get_admin_urls
    from fastadmin.settings import settings

    urlpatterns = [
        path(f"{settings.ADMIN_PREFIX}/", get_admin_urls()),
    ]
    ```

## 2. Register a model admin

Register the ORM model named by `ADMIN_USER_MODEL` first — it is required for
sign-in. Pick the admin base class matching your ORM
(`TortoiseModelAdmin`, `DjangoModelAdmin`, `SqlAlchemyModelAdmin` or
`PonyORMModelAdmin`):

```python
import bcrypt

from fastadmin import TortoiseModelAdmin, register

from models import User


@register(User)
class UserAdmin(TortoiseModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    async def authenticate(self, username: str, password: str) -> int | None:
        user = await User.filter(username=username, is_superuser=True).first()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return None
        return user.id

    async def change_password(self, id: int, password: str) -> None:
        user = await User.filter(id=id).first()
        if not user:
            return
        user.hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        await user.save(update_fields=("hash_password",))
```

!!! warning

    The model admin for `ADMIN_USER_MODEL` **must** implement `authenticate`
    (and `change_password` if you want password editing). See
    [Authentication](../guides/authentication.md).

## 3. Run it

Start your app as usual (e.g. `uvicorn example:app` for FastAPI) and open
`http://localhost:8000/admin`. Sign in with a user for which `authenticate`
returns an id.

## Next steps

- [Registering models](../guides/registering-models.md) — complete, runnable
  examples for all four ORMs.
- [Model admins](../guides/model-admins.md) — all attributes and hooks
  (`list_display`, actions, permissions, exports, …).
- [Dashboard widgets](../guides/dashboard-widgets.md) — add charts to the
  dashboard.
