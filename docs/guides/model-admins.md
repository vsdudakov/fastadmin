---
title: Model admins
description: All ModelAdmin attributes and methods — list display, filters, search, ordering, actions, display fields, exports and save hooks.
---

# Model admins

A model admin controls how a model appears and behaves in the dashboard. All
attributes are optional and mirror Django Admin where possible.

## List page attributes

| Attribute | Default | Description |
| --- | --- | --- |
| `list_display` | `()` | Fields shown as columns on the list page. Without it, a single `__str__` column is shown. |
| `list_display_links` | `()` | Which `list_display` fields link to the change page. |
| `list_display_widths` | `{}` | Column widths per field (`{"id": "100px"}`). |
| `list_display_labels` | `{}` | Column headers per field (`{"id": "Идентификатор"}`) — use to override or translate the auto-generated titles. |
| `list_filter` | `()` | Fields that get a filter in the table columns. |
| `list_per_page` | `10` | Items per paginated page. |
| `list_max_show_all` | `200` | Max total count for which a "Show all" link is displayed. |
| `list_select_related` | `()` | Relations passed to the ORM's `select_related` to save queries. |
| `ordering` | `()` | Default ordering, e.g. `("-created_at",)`. |
| `preserve_filters` | `True` | Keep applied filters after add/edit/delete. |
| `search_fields` | `()` | Fields searched by the search box. |
| `search_help_text` | `""` | Help text under the search box. |
| `show_full_result_count` | `False` | Show "99 results (103 total)" on filtered pages. |
| `sortable_by` | `()` | Restrict sortable columns (empty = all sortable). |
| `empty_value_display` | `"-"` | Display value for empty fields. |
| `verbose_name` / `verbose_name_plural` | `None` | Override the model's display name. |
| `menu_section` | `None` | Group the model under a section in the left menu. |
| `model_name_prefix` | `None` | Prefix to disambiguate models when using several ORMs. |

## Form page attributes

| Attribute | Default | Description |
| --- | --- | --- |
| `fields` | `()` | Subset/order of fields on add/change forms. |
| `fieldsets` | `()` | Two-tuples grouping fields into form sections. |
| `exclude` | `()` | Fields to exclude from the form. |
| `readonly_fields` | `()` | Fields rendered non-editable. |
| `formfield_overrides` | `{}` | Per-field widget overrides — see [Form widgets](form-widgets.md). |
| `filter_horizontal` / `filter_vertical` | `()` | Use a search-friendly two-box UI for M2M fields. |
| `radio_fields` | `()` | Use radio buttons instead of a select for FK/choice fields. |
| `raw_id_fields` | `()` | Use a plain input instead of a select for FK/M2M fields. |
| `save_as` | `False` | Replace "Save and add another" with "Save as new". |
| `save_as_continue` | `False` | Where "Save as new" redirects: the changelist by default, or the new object's change view when `True`. |
| `save_on_top` | `False` | Show save buttons at the top of the form too. |
| `view_on_site` | `None` | URL for a "View on site" link. |
| `inlines` | `()` | Inline admin classes — see [Inline admins](inline-admins.md). |

## Actions

Define bulk actions with the `@action` decorator and list them in `actions`:

```python
from fastadmin import TortoiseModelAdmin, action, register
from fastadmin import ActionResponseSchema, ActionResponseType


@register(Story)
class StoryAdmin(TortoiseModelAdmin):
    actions = ("make_published",)
    actions_on_top = False        # actions bar at the top of the list page
    actions_on_bottom = True      # actions bar at the bottom
    actions_selection_counter = True

    @action(description="Mark selected stories as published")
    async def make_published(self, objs: list) -> ActionResponseSchema | None:
        for obj in objs:
            obj.status = "published"
            await obj.save()
        return ActionResponseSchema(type=ActionResponseType.MESSAGE, data="Published!")
```

An action can return `None`, a `MESSAGE` response, or a `DOWNLOAD_BASE64`
response (`data` is base64 file content, `file_name` names the download).

By default the Apply button is disabled until at least one row is selected.
Pass `requires_selection=False` to allow running an action without selecting
rows — the action then receives an empty `ids` list and should treat it as
"all objects":

```python
    @action(description="Delete all stories", requires_selection=False)
    async def delete_all(self, ids: list) -> None:
        await Story.all().delete()
```

## Display fields

Add computed, read-only columns with the `@display` decorator and include
them in `list_display`:

```python
from fastadmin import display


class EventAdmin(TortoiseModelAdmin):
    list_display = ("id", "name", "is_published", "author")

    @display
    async def is_published(self, obj):
        return obj.publish_date is not None

    @display(sorter="user__username")  # sortable by a related field
    async def author(self, obj):
        return (await obj.user).username
```

`sorter=True` sorts by the function name as a field; a string sorts by that
ORM expression.

!!! warning

    String `sorter` expressions are supported only for Django and Tortoise ORM.

## Save / delete hooks

Override these to customize persistence (always call `super()` unless you
replace the behavior entirely):

```python
class EventAdmin(TortoiseModelAdmin):
    async def save_model(self, id, payload: dict) -> dict | None:
        payload["updated_by"] = self.user["id"] if self.user else None
        return await super().save_model(id, payload)

    async def delete_model(self, id) -> None:
        await super().delete_model(id)
```

Other useful hooks:

- `orm_get_list(offset, limit, search, sort_by, filters)` — low-level list
  query; override for custom querysets.
- `serialize_obj(obj, list_view=False)` — object → dict serialization.
- `pre_generate_models_schema()` — pre-generate the models schema (e.g. warm
  caches) before the configuration is served.
- `get_export(...)` — CSV/JSON export used by the export button (gate it with
  `has_export_permission`).

## Custom value encoders

By default, model field values are serialized to JSON with sensible built-ins:
`datetime`/`date`/`time` become ISO 8601 strings, `UUID`s become strings, and
`Decimal`s are rendered without scientific notation.

Register a custom encoder to control how a given type is represented in **every**
admin API response — for example a custom datetime format, an `Enum`'s label, or a
domain value object:

```python
import datetime

from fastadmin import register_encoder

# Render every datetime as "2024-01-31 14:05" instead of ISO 8601.
register_encoder(datetime.datetime, lambda dt: dt.strftime("%Y-%m-%d %H:%M"))
```

Encoders are matched via `isinstance` in registration order (register more
specific types before their base types) and take precedence over the built-in
handling. Use `unregister_encoder(type_)` to remove one.

## Permissions and request context

See [Authentication](authentication.md#permissions) for
`has_add/change/delete/export_permission` and the `self.request` /
`self.user` context.

The full class reference lives in the
[API reference](../api-reference.md).
