---
title: API reference
description: Public API of the fastadmin package — apps, admin classes, decorators, registry helpers and schemas.
---

# API reference

Everything documented here is importable from the top-level `fastadmin`
package.

## Framework apps

| Export | Available with extra | Description |
| --- | --- | --- |
| `fastapi_app` | `fastadmin[fastapi]` | ASGI sub-application — `app.mount("/admin", fastapi_app)`. |
| `flask_app` | `fastadmin[flask]` | Flask blueprint — `app.register_blueprint(flask_app, url_prefix="/admin")`. |
| `get_django_admin_urls()` | `fastadmin[django]` | Django url patterns — `path("admin/", get_django_admin_urls())`. |

## Admin classes

| Export | Description |
| --- | --- |
| `ModelAdmin` | ORM-agnostic base model admin. |
| `InlineModelAdmin` | ORM-agnostic base inline admin. |
| `TortoiseModelAdmin` / `TortoiseInlineModelAdmin` | Tortoise ORM admins. |
| `DjangoModelAdmin` / `DjangoInlineModelAdmin` | Django ORM admins. |
| `SqlAlchemyModelAdmin` / `SqlAlchemyInlineModelAdmin` | SQLAlchemy (async) admins. |
| `PonyORMModelAdmin` / `PonyORMInlineModelAdmin` | Pony ORM admins. |
| `YaraOrmModelAdmin` / `YaraOrmInlineModelAdmin` | [Yara ORM](https://github.com/vsdudakov/yara-orm) admins. |

Attributes are documented in [Model admins](guides/model-admins.md) and
[Inline admins](guides/inline-admins.md).

### BaseModelAdmin methods

Overridable hooks (shared by model and inline admins):

| Method | Description |
| --- | --- |
| `async orm_get_list(offset, limit, search, sort_by, filters)` | Low-level list query; returns `(objects, total)`. |
| `async orm_get_obj(id)` | Fetch a single object or `None`. |
| `async orm_save_obj(id, payload)` | Create (`id=None`) or update an object. |
| `async orm_delete_obj(id)` | Delete an object. |
| `async orm_get_m2m_ids(obj, field)` / `orm_save_m2m_ids(obj, field, ids)` | Read/write M2M relations. |
| `async get_list(...)` | Serialized list used by the list page. |
| `async get_obj(id)` | Serialized object used by the change page. |
| `async save_model(id, payload)` | Save hook (deserializes, saves, handles M2M). |
| `async delete_model(id)` | Delete hook. |
| `async serialize_obj(obj, list_view=False)` | Object → dict serialization. |
| `resolve_sort_by(sort_by)` | Map a display-column sort to an ORM expression. |
| `async pre_generate_models_schema()` | Pre-generate the models schema. |
| `async get_export(export_format, ...)` | Build the CSV/JSON export stream. |
| `async upload_file(field_name, file_name, file_content, obj=None)` | Store an uploaded file; returns the stored URL/key. |
| `async get_file_url(field_name, value, obj=None)` | Display URL for an upload field (`{field}__url` / `valueRepr`). |
| `async has_add_permission(user_id=None)` | Gate the add button. |
| `async has_change_permission(user_id=None)` | Gate editing. |
| `async has_delete_permission(user_id=None)` | Gate deletion. |
| `async has_export_permission(user_id=None)` | Gate exports. |
| `request` / `user` (properties) | Request-scoped context for the current call. |
| `get_sessionmaker()` / `set_sessionmaker(maker)` | SQLAlchemy session maker accessors. |

### ModelAdmin-only methods

| Method | Description |
| --- | --- |
| `async authenticate(username, password)` | Return a user id or `None`. Required on the `ADMIN_USER_MODEL` admin. |
| `async change_password(id, password)` | Store a new (hashed) password. |

## Decorators

| Export | Description |
| --- | --- |
| `@register(*models, **kwargs)` | Register a `ModelAdmin` subclass for the given model(s). For SQLAlchemy pass `sqlalchemy_sessionmaker=...`. |
| `@action(description=None)` | Mark an admin method as a bulk action (list it in `actions`). |
| `@display(sorter=False)` | Mark an admin method as a computed list column (include it in `list_display`). |
| `@widget_action(...)` | Mark an admin method as a dashboard widget (list it in `widget_actions`). See [Dashboard widgets](guides/dashboard-widgets.md). |

## Registry helpers

| Export | Description |
| --- | --- |
| `register_admin_model_class(admin_cls, models, **kwargs)` | Imperative registration. |
| `unregister_admin_model_class(models)` | Remove models from the registry. |

## Enums

| Export | Values |
| --- | --- |
| `WidgetType` | `Input`, `InputNumber`, `SlugInput`, `EmailInput`, `PhoneInput`, `UrlInput`, `PasswordInput`, `TextArea`, `RichTextArea`, `JsonTextArea`, `Select`, `AsyncSelect`, `AsyncTransfer`, `Switch`, `Checkbox`, `TimePicker`, `DatePicker`, `DateTimePicker`, `RangePicker`, `RadioGroup`, `CheckboxGroup`, `UploadFile`, `UploadImage` |
| `WidgetActionType` | `ChartLine`, `ChartArea`, `ChartColumn`, `ChartBar`, `ChartPie`, `Action` |
| `ActionResponseType` | `DOWNLOAD_BASE64`, `MESSAGE` |

## Schemas

| Export | Description |
| --- | --- |
| `ActionInputSchema` | Input to `@action` handlers: `ids` of the selected objects. |
| `ActionResponseSchema` | Action result: `type` (`ActionResponseType`), `data`, optional `file_name`. |
| `WidgetActionInputSchema` | Input to `@widget_action` handlers: `query` — a list of `WidgetActionQuerySchema`. |
| `WidgetActionQuerySchema` | One filter/argument value: `field_name`, `widget_type`, `value`. |
| `WidgetActionResponseSchema` | Widget result: `data` — a list of row dicts. |
| `WidgetActionChartProps` | Chart mapping: `x_field`, `y_field`, `series_field`, `series_color`. |
| `WidgetActionProps` | Action form: `arguments` — a list of `WidgetActionArgumentProps`. |
| `WidgetActionArgumentProps` | One form argument: `name`, `widget_type`, `widget_props`, `parent_argument`. |
| `WidgetActionParentArgumentProps` | Conditional visibility: `name`, `value`. |
| `WidgetActionFilter` | One widget filter: `field_name`, `widget_type`, `widget_props`. |
| `ModelWidgetAction` | Serialized widget metadata (as exposed to the frontend). |

## Exceptions

| Export | Description |
| --- | --- |
| `AdminApiException` | Raise from admin hooks to return an API error (`status_code`, `detail`). |

## Settings

Runtime configuration is read from environment variables — see
[Settings](guides/settings.md). The parsed values are available as
`fastadmin.settings.settings`.
