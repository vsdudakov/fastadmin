---
title: Form widgets & file uploads
description: FastAdmin form widget types, formfield_overrides, and file/image uploads with custom storage and display URLs.
---

# Form widgets & file uploads

## Widget types

FastAdmin renders form fields with [antd](https://ant.design/components/overview)
components. Every widget type is available via the `WidgetType` enum:

| Widget | Renders as |
| --- | --- |
| `Input` | Single-line text input |
| `InputNumber` | Numeric input |
| `SlugInput` | Slug input (auto-slugified) |
| `EmailInput` | Email input |
| `PhoneInput` | Phone input with country codes |
| `UrlInput` | URL input |
| `PasswordInput` | Password input (on create, the value is stored via `change_password`) |
| `TextArea` | Multi-line text |
| `RichTextArea` | Rich-text (WYSIWYG) editor |
| `JsonTextArea` | JSON editor |
| `Select` | Select box |
| `AsyncSelect` | Select with async search (default for FK/M2M) |
| `AsyncTransfer` | Transfer (two-box) widget with async search |
| `Switch` | On/off switch |
| `Checkbox` | Checkbox |
| `TimePicker` | Time picker (`ADMIN_TIME_FORMAT`) |
| `DatePicker` | Date picker (`ADMIN_DATE_FORMAT`) |
| `DateTimePicker` | Datetime picker (`ADMIN_DATETIME_FORMAT`) |
| `RangePicker` | Date range picker |
| `RadioGroup` | Radio buttons |
| `CheckboxGroup` | Checkbox group |
| `UploadFile` | File upload |
| `UploadImage` | Image upload (with crop; disable via `disableCropImage` prop) |

## formfield_overrides

Use `formfield_overrides` to pick a widget and props per field. `label` sets a
custom field label and `help` shows description text below the field; other
props are passed to the antd component:

```python
from fastadmin import TortoiseModelAdmin, WidgetType, register


@register(User)
class UserAdmin(TortoiseModelAdmin):
    formfield_overrides = {
        "username": (
            WidgetType.SlugInput,
            {
                "required": True,
                "label": "Custom label",
                "help": "Detailed description of the field",
            },
        ),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
        "bio": (WidgetType.RichTextArea, {}),
        "avatar_url": (WidgetType.UploadImage, {"disableCropImage": True}),
    }
```

## File uploads

For file and image fields use the `UploadFile` / `UploadImage` widgets in
`formfield_overrides` and implement `upload_file` on the model admin. It
receives the raw file and must return the URL (or key) to store in the field —
e.g. after saving to disk or S3:

```python
class UserAdmin(TortoiseModelAdmin):
    formfield_overrides = {
        "attachment": (WidgetType.UploadFile, {"required": False}),
    }

    async def upload_file(
        self,
        field_name: str,
        file_name: str,
        file_content: bytes,
        obj=None,  # None on the add page; the existing instance on the change page
    ) -> str:
        path = Path("uploads") / file_name
        path.write_bytes(file_content)
        return f"/uploads/{file_name}"
```

### Custom display URLs (get_file_url)

To customize the URL shown in the upload widget — e.g. generate an S3
presigned URL instead of displaying the raw `s3://` key — override
`get_file_url`. The display URL is emitted as `{field_name}__url` in the
serialized object and passed to the widget as `valueRepr`; the raw stored
value is never changed, so form saves are unaffected:

```python
async def get_file_url(self, field_name: str, value: str, obj=None) -> str:
    # value is the raw stored key, e.g. "s3://bucket/key"
    bucket, key = value.replace("s3://", "").split("/", 1)
    async with aiobotocore.session.get_session().create_client("s3") as s3:
        return await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,
        )
```
