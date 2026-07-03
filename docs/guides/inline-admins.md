---
title: Inline admins
description: Edit related models on the same page with FastAdmin inline model admins.
---

# Inline admins

Inline admins let you edit related objects on the parent model's change page —
like Django Admin's `TabularInline`. Define a class inheriting the inline
admin for your ORM (`TortoiseInlineModelAdmin`, `DjangoInlineModelAdmin`,
`SqlAlchemyInlineModelAdmin` or `PonyORMInlineModelAdmin`) and list it in the
parent admin's `inlines`:

```python
from fastadmin import TortoiseInlineModelAdmin, TortoiseModelAdmin, register

from models import Tournament, Event


class EventInline(TortoiseInlineModelAdmin):
    model = Event
    list_display = ("id", "name", "start_time")
    max_num = 5


@register(Tournament)
class TournamentAdmin(TortoiseModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInline,)
```

Inline admins support all the [BaseModelAdmin attributes and
hooks](model-admins.md) (`list_display`, `list_filter`, `search_fields`,
`formfield_overrides`, `upload_file`, permissions, …) plus:

| Attribute | Default | Description |
| --- | --- | --- |
| `model` | — | The related model class the inline edits. **Required.** |
| `fk_name` | `None` | Name of the foreign key to the parent. Usually detected automatically; set it explicitly when the model has more than one FK to the same parent. |
| `max_num` | `10` | Maximum number of forms shown in the inline. |
| `min_num` | `1` | Minimum number of forms shown in the inline. |

For complete runnable examples (including M2M inlines across all four ORMs),
see [Registering models](registering-models.md#complete-examples).
