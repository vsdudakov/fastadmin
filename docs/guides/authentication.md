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
  id (`int` or `UUID`) or `None`.
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

Permission hooks are enforced **server-side**: `add`, `change`, `delete` and
`export` requests each call the matching hook and return `403` if it returns
`False`, so disabling an action is not merely cosmetic. Similarly,
`change_password` only allows changing another user's password when
`has_change_permission` grants it (users can always change their own).

## Security considerations

FastAdmin ships secure defaults, but a few things are the deployer's
responsibility:

- **Strong secret key** — set `ADMIN_SECRET_KEY` to a long, random value
  (≥ 32 bytes). It signs the session JWT.
- **HTTPS** — keep `ADMIN_SESSION_COOKIE_SECURE=true` (the default) in
  production so the session cookie is never sent over plain HTTP.
- **Sign-out is not token revocation** — the session is a stateless JWT, so
  sign-out clears the cookie but a copy of the token stays valid until it
  expires (`ADMIN_SESSION_EXPIRED_AT`). Keep the lifetime modest; to force-
  invalidate all sessions, rotate `ADMIN_SECRET_KEY`.
- **Rate limiting** — FastAdmin does not throttle sign-in. Put a rate limiter
  in front of `/{ADMIN_PREFIX}/api/sign-in` to slow credential stuffing, and
  use a constant-time password comparison in `authenticate`.
- **Limit what can be filtered** — set `list_filter` (or `fields`/`exclude`) so
  requests can only filter on columns you intend to expose; otherwise every
  serialized column is filterable.
