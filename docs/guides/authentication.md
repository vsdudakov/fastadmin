---
title: Authentication
description: Implement sign-in and password changes for the FastAdmin dashboard user model.
---

# Authentication

FastAdmin authenticates against the ORM model named by the
`ADMIN_USER_MODEL` setting. The model admin registered for that model **must**
implement `authenticate`; implement `change_password` as well if you want the
"change password" feature (and hashed passwords on create).

```python
import bcrypt

from fastadmin import TortoiseModelAdmin, register

from models import User


@register(User)
class UserAdmin(TortoiseModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    async def authenticate(self, username: str, password: str) -> int | None:
        """Return the user id on success, or None to reject the sign-in."""
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

- `authenticate(username, password)` receives the value of the
  `ADMIN_USER_MODEL_USERNAME_FIELD` field and the password, and returns a user
  id (`int`, `str` or `UUID`) or `None`.
- `change_password(id, password)` stores a new password. FastAdmin also calls
  it automatically after creating an object whose form contains a
  `PasswordInput` widget, so passwords are stored hashed.

On successful sign-in, FastAdmin stores a signed session id (using
`ADMIN_SECRET_KEY`) in an HTTP-only cookie (`ADMIN_SESSION_ID_KEY`,
expiring after `ADMIN_SESSION_EXPIRED_AT` seconds).

## Permissions

Model admins expose per-action permission hooks — return `False` to hide the
corresponding functionality for the current user:

```python
class EventAdmin(TortoiseModelAdmin):
    async def has_add_permission(self, user_id=None) -> bool: ...
    async def has_change_permission(self, user_id=None) -> bool: ...
    async def has_delete_permission(self, user_id=None) -> bool: ...
    async def has_export_permission(self, user_id=None) -> bool: ...
```

Inside any admin method you can use the request-scoped context:

```python
class EventAdmin(TortoiseModelAdmin):
    async def has_change_permission(self, user_id=None):
        # self.request / self.user hold the current request context
        return bool(self.user and self.user.get("is_superuser"))

    async def save_model(self, id, payload):
        if self.request:
            payload["changed_from_ip"] = getattr(self.request, "client", None)
        return await super().save_model(id, payload)
```
