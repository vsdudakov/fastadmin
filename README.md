<h1 align="center">FastAdmin — Admin Dashboard for FastAPI, Flask and Django</h1>

<p align="center">
  <a href="https://github.com/vsdudakov/fastadmin/actions/workflows/ci.yml"><img src="https://github.com/vsdudakov/fastadmin/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://app.codecov.io/gh/vsdudakov/fastadmin"><img src="https://codecov.io/gh/vsdudakov/fastadmin/branch/main/graph/badge.svg?token=RNGX5HOW3T" alt="codecov"></a>
  <a href="https://pypi.org/project/fastadmin/"><img src="https://badgen.net/pypi/v/fastadmin" alt="PyPI"></a>
  <a href="https://pypi.org/project/fastadmin/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg" alt="Python 3.12+"></a>
  <a href="https://github.com/vsdudakov/fastadmin/blob/main/LICENSE.md"><img src="https://img.shields.io/github/license/vsdudakov/fastadmin" alt="License: MIT"></a>
</p>

**FastAdmin** is an easy-to-use **admin dashboard (admin panel) for FastAPI, Flask and
Django**, inspired by Django Admin. It gives your Python web application a
production-ready **CRUD admin interface** in minutes — on top of **Tortoise ORM,
Django ORM, SQLAlchemy or Pony ORM** — with authentication, filters, search,
inline editing, file uploads, CSV/JSON export and dashboard charts out of the box.

FastAdmin is built with relationships in mind and admiration for Django Admin.
It aims to be minimal, functional and familiar: if you know Django Admin, you
already know FastAdmin.

📚 **Documentation: [https://vsdudakov.github.io/fastadmin/](https://vsdudakov.github.io/fastadmin/)**

## Demo

![FastAdmin demo — admin panel for FastAPI, Flask and Django](https://raw.githubusercontent.com/vsdudakov/fastadmin/main/docs/assets/images/demo.gif)

## Features

- **Familiar Django-Admin-style API** — `list_display`, `list_filter`,
  `search_fields`, `fieldsets`, `readonly_fields`, inlines, actions and more.
- **Any web framework** — mount as a FastAPI sub-app, a Flask blueprint or
  Django urlpatterns.
- **Any ORM** — first-class admin classes for Tortoise ORM, Django ORM,
  SQLAlchemy (async) and Pony ORM.
- **Authentication & permissions** — pluggable sign-in against your own user
  model, per-action permission hooks, request/user context in every admin method.
- **Rich form widgets** — 20+ antd-based widgets (rich text, JSON, async
  select, phone, slug, date/time pickers, switches, radio groups, …) via
  `formfield_overrides`.
- **File & image uploads** — storage-agnostic `upload_file` hook and
  presigned-URL support via `get_file_url` (local disk, S3, …).
- **Dashboard widgets** — declarative line/area/column/bar/pie charts and
  action widgets with filters, powered by antd charts.
- **Bulk actions & export** — custom bulk actions, CSV/JSON export.
- **Quality** — fully typed and linted (ruff + ty), 100% backend test coverage,
  modern React (Vite + antd) frontend bundled with the package — no Node.js
  needed at install time.

## Installation

Install with the extras matching your web framework and ORM (each combination
works standalone):

```bash
pip install fastadmin[fastapi,django]        # FastAPI with Django ORM
pip install fastadmin[fastapi,tortoise-orm]  # FastAPI with Tortoise ORM
pip install fastadmin[fastapi,pony]          # FastAPI with Pony ORM
pip install fastadmin[fastapi,sqlalchemy]    # FastAPI with SQLAlchemy (includes greenlet)
pip install fastadmin[django]                # Django with Django ORM
pip install fastadmin[django,pony]           # Django with Pony ORM
pip install fastadmin[flask,sqlalchemy]      # Flask with SQLAlchemy (includes greenlet)
```

> **Note:** on zsh (the default macOS shell) quote the extras: `pip install 'fastadmin[fastapi,django]'`.

Configure the required settings:

```bash
export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key
```

## Quick start

```python
import bcrypt
from fastapi import FastAPI

from fastadmin import TortoiseModelAdmin, register
from fastadmin import fastapi_app as admin_app

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


app = FastAPI()
app.mount("/admin", admin_app)
```

Run `uvicorn example:app` and open `http://localhost:8000/admin`.

Mounting for the other frameworks:

```python
# Flask
from fastadmin import flask_app as admin_app
app.register_blueprint(admin_app, url_prefix="/admin")

# Django (urls.py)
from fastadmin import get_django_admin_urls as get_admin_urls
urlpatterns = [path("admin/", get_admin_urls())]
```

## Documentation

Full documentation lives at
**[vsdudakov.github.io/fastadmin](https://vsdudakov.github.io/fastadmin/)**:

- [Installation](https://vsdudakov.github.io/fastadmin/getting-started/installation/)
  and [Quick start](https://vsdudakov.github.io/fastadmin/getting-started/quickstart/)
- [Settings](https://vsdudakov.github.io/fastadmin/guides/settings/) — all environment variables
- [Registering models](https://vsdudakov.github.io/fastadmin/guides/registering-models/) — complete runnable examples for all four ORMs
- [Authentication](https://vsdudakov.github.io/fastadmin/guides/authentication/) and permissions
- [Model admins](https://vsdudakov.github.io/fastadmin/guides/model-admins/) — attributes, actions, display fields, exports
- [Form widgets & file uploads](https://vsdudakov.github.io/fastadmin/guides/form-widgets/)
- [Inline admins](https://vsdudakov.github.io/fastadmin/guides/inline-admins/)
- [Dashboard widgets](https://vsdudakov.github.io/fastadmin/guides/dashboard-widgets/) — charts and actions
- [API reference](https://vsdudakov.github.io/fastadmin/api-reference/)

Runnable example apps for every framework/ORM combination are in
[`examples/`](https://github.com/vsdudakov/fastadmin/tree/main/examples).

## Why FastAdmin?

If you are looking for a **Django-Admin-like admin panel for FastAPI**, an
**admin interface for SQLAlchemy or Tortoise ORM**, or a lightweight
**alternative to building a custom back office**, FastAdmin gives you a
batteries-included, themeable admin UI without code generation, without tying
your app to a specific framework, and without writing a single React component.

## Contributing

Contributions are welcome — see the
[contributing guide](https://vsdudakov.github.io/fastadmin/contributing/).
Development uses `uv` and `make`: `make dev`, `make lint`, `make test`.
See [CHANGELOG.md](https://github.com/vsdudakov/fastadmin/blob/main/CHANGELOG.md)
for release history.

If you have questions beyond the documentation, feel free to
[email us](mailto:vsdudakov@gmail.com).

## License

FastAdmin is released under the
[MIT License](https://github.com/vsdudakov/fastadmin/blob/main/LICENSE.md).
