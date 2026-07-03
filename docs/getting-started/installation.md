---
title: Installation
description: How to install FastAdmin with pip, uv or poetry for FastAPI, Flask or Django with Tortoise ORM, Django ORM, SQLAlchemy or Pony ORM.
---

# Installation

FastAdmin requires **Python 3.12+**.

Install the package with the extras matching your web framework and ORM:

=== "pip"

    ```bash
    pip install fastadmin[fastapi,django]        # FastAPI with Django ORM
    pip install fastadmin[fastapi,tortoise-orm]  # FastAPI with Tortoise ORM
    pip install fastadmin[fastapi,pony]          # FastAPI with Pony ORM
    pip install fastadmin[fastapi,sqlalchemy]    # FastAPI with SQLAlchemy (includes greenlet)
    pip install fastadmin[django]                # Django with Django ORM
    pip install fastadmin[django,pony]           # Django with Pony ORM
    pip install fastadmin[flask,sqlalchemy]      # Flask with SQLAlchemy (includes greenlet)
    ```

=== "uv"

    ```bash
    uv add 'fastadmin[fastapi,django]'
    uv add 'fastadmin[fastapi,tortoise-orm]'
    uv add 'fastadmin[fastapi,pony]'
    uv add 'fastadmin[fastapi,sqlalchemy]'
    uv add 'fastadmin[django]'
    uv add 'fastadmin[django,pony]'
    uv add 'fastadmin[flask,sqlalchemy]'
    ```

=== "poetry"

    ```bash
    poetry add 'fastadmin[fastapi,django]'
    poetry add 'fastadmin[fastapi,tortoise-orm]'
    poetry add 'fastadmin[fastapi,pony]'
    poetry add 'fastadmin[fastapi,sqlalchemy]'
    poetry add 'fastadmin[django]'
    poetry add 'fastadmin[django,pony]'
    poetry add 'fastadmin[flask,sqlalchemy]'
    ```

!!! tip

    On zsh (the default macOS shell), quote the extras:
    `pip install 'fastadmin[fastapi,django]'`

!!! info

    When using SQLAlchemy, the `greenlet` package is required — it is included
    in the `fastadmin[sqlalchemy]` extra.

## Required settings

Configure the required settings as environment variables:

```bash
export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key
```

!!! info

    You can put these variables in a `.env` file and load them with
    [python-dotenv](https://pypi.org/project/python-dotenv/). See
    [Settings](../guides/settings.md) for the full list of options.

Next, follow the [Quick start](quickstart.md) to mount the dashboard and
register your first model.
