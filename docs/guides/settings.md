---
title: Settings
description: All FastAdmin environment variables — required settings and defaults.
---

# Settings

FastAdmin is configured entirely through environment variables. Set them in
your shell, your process manager, or a `.env` file loaded with
[python-dotenv](https://pypi.org/project/python-dotenv/).

## Required settings

These have no defaults and must be set:

| Variable | Description |
| --- | --- |
| `ADMIN_USER_MODEL` | Name of the user db/orm model class used for authentication (e.g. `User`). |
| `ADMIN_USER_MODEL_USERNAME_FIELD` | Username field on the user model (e.g. `username` or `email`). |
| `ADMIN_SECRET_KEY` | Key used to sign session data. Keep it secret — anyone holding it can forge signed values. |

```bash
export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key
```

## Optional settings

| Variable | Default | Description |
| --- | --- | --- |
| `ADMIN_PREFIX` | `admin` | URL prefix the admin app is mounted under. |
| `ADMIN_SITE_NAME` | `FastAdmin` | Site name shown on the sign-in page and header. |
| `ADMIN_SITE_SIGN_IN_LOGO` | `/admin/static/images/sign-in-logo.svg` | Logo path on the sign-in page. |
| `ADMIN_SITE_HEADER_LOGO` | `/admin/static/images/header-logo.svg` | Logo path in the header. |
| `ADMIN_SITE_FAVICON` | `/admin/static/images/favicon.png` | Favicon path. |
| `ADMIN_PRIMARY_COLOR` | `#009485` | Primary UI color. |
| `ADMIN_SESSION_ID_KEY` | `admin_session_id` | Cookie key for the session id (HTTP-only). |
| `ADMIN_SESSION_EXPIRED_AT` | `144000` | Session lifetime in seconds. |
| `ADMIN_DATE_FORMAT` | `YYYY-MM-DD` | Date format for JS widgets. |
| `ADMIN_DATETIME_FORMAT` | `YYYY-MM-DD HH:mm` | Datetime format for JS widgets. |
| `ADMIN_TIME_FORMAT` | `HH:mm:ss` | Time format for JS widgets. |

The authoritative source is the `Settings` class:

```python
--8<-- "fastadmin/settings.py"
```
