---
title: Registering models
description: Register ORM models with FastAdmin — complete runnable examples for Tortoise ORM, Django ORM, SQLAlchemy and Pony ORM.
---

# Registering models

Register a model by decorating a model admin class with `@register(Model)`.
The admin base class must match your ORM:

| ORM | Model admin | Inline admin |
| --- | --- | --- |
| Tortoise ORM | `TortoiseModelAdmin` | `TortoiseInlineModelAdmin` |
| Django ORM | `DjangoModelAdmin` | `DjangoInlineModelAdmin` |
| SQLAlchemy | `SqlAlchemyModelAdmin` | `SqlAlchemyInlineModelAdmin` |
| Pony ORM | `PonyORMModelAdmin` | `PonyORMInlineModelAdmin` |

```python
from fastadmin import TortoiseModelAdmin, register

from models import Tournament


@register(Tournament)
class TournamentAdmin(TortoiseModelAdmin):
    list_display = ("id", "name")
```

!!! info

    For SQLAlchemy, pass the async session maker when registering:
    `@register(Model, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)`.

You can also register and unregister imperatively with
`register_admin_model_class(AdminCls, [Model])` and
`unregister_admin_model_class([Model])`.

!!! tip

    If you mix several ORMs in one project, set `model_name_prefix` on the
    model admin to avoid name collisions.

## Complete examples

Each tab below is a full, runnable application from the
[`examples/`](https://github.com/vsdudakov/fastadmin/tree/main/examples)
folder of the repository — models, admins (with inlines, actions, display
fields, uploads and dashboard widgets), authentication and app mounting.

=== "Tortoise ORM"

    ```python
    --8<-- "examples/fastapi_tortoiseorm/example.py"
    ```

=== "Django ORM"

    ```python
    --8<-- "examples/django_djangoorm/orm/models.py"
    ```

=== "SQLAlchemy"

    ```python
    --8<-- "examples/fastapi_sqlalchemy/example.py"
    ```

=== "Pony ORM"

    ```python
    --8<-- "examples/fastapi_ponyorm/example.py"
    ```
