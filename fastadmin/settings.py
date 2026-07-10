import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent


def _env_int(name: str, default: int) -> int:
    """Read an int env var, falling back to the default when it is unset, blank, or non-numeric.

    ``int(os.getenv(...))`` crashes the whole package at import time on an empty
    (``NAME=``) or garbage value, so parse defensively instead.
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class Settings:
    """Settings"""

    # This value is the prefix you used for mounting FastAdmin app for FastAPI.
    ADMIN_PREFIX: str = os.getenv("ADMIN_PREFIX", "admin")

    # This value is the site name on sign-in page and on header.
    ADMIN_SITE_NAME: str = os.getenv("ADMIN_SITE_NAME", "FastAdmin")

    # This value is the logo path on sign-in page.
    ADMIN_SITE_SIGN_IN_LOGO: str = os.getenv("ADMIN_SITE_SIGN_IN_LOGO", "/admin/static/images/sign-in-logo.svg")

    # This value is the logo path on header.
    ADMIN_SITE_HEADER_LOGO: str = os.getenv("ADMIN_SITE_HEADER_LOGO", "/admin/static/images/header-logo.svg")

    # This value is the favicon path.
    ADMIN_SITE_FAVICON: str = os.getenv("ADMIN_SITE_FAVICON", "/admin/static/images/favicon.png")

    # This value is the primary color for FastAdmin.
    ADMIN_PRIMARY_COLOR: str = os.getenv("ADMIN_PRIMARY_COLOR", "#009485")

    # This value is the session id key to store session id in http only cookies.
    ADMIN_SESSION_ID_KEY: str = os.getenv("ADMIN_SESSION_ID_KEY", "admin_session_id")

    # This value is the expired_at period (in sec) for session id.
    ADMIN_SESSION_EXPIRED_AT: int = _env_int("ADMIN_SESSION_EXPIRED_AT", 144000)  # in sec

    # Set the Secure flag on the session cookie so it is only sent over HTTPS.
    # Enabled by default; set ADMIN_SESSION_COOKIE_SECURE=false for local HTTP dev.
    ADMIN_SESSION_COOKIE_SECURE: bool = os.getenv("ADMIN_SESSION_COOKIE_SECURE", "true").lower() != "false"

    # SameSite policy for the session cookie ("lax", "strict" or "none").
    # "lax" blocks the cross-site POST/PATCH/DELETE requests behind CSRF.
    ADMIN_SESSION_COOKIE_SAMESITE: str = os.getenv("ADMIN_SESSION_COOKIE_SAMESITE", "lax")

    # Hard upper bound on the number of rows a single list/export request may
    # return. Caps memory/CPU use from a crafted limit=100000000 request.
    ADMIN_QUERY_MAX_LIMIT: int = _env_int("ADMIN_QUERY_MAX_LIMIT", 1000)

    # This value is the date format for JS widgets.
    ADMIN_DATE_FORMAT: str = os.getenv("ADMIN_DATE_FORMAT", "YYYY-MM-DD")

    # This value is the datetime format for JS widgets.
    ADMIN_DATETIME_FORMAT: str = os.getenv("ADMIN_DATETIME_FORMAT", "YYYY-MM-DD HH:mm")

    # This value is the time format for JS widgets.
    ADMIN_TIME_FORMAT: str = os.getenv("ADMIN_TIME_FORMAT", "HH:mm:ss")

    # This value is the name for User db/orm model class for authentication.
    ADMIN_USER_MODEL: str = os.getenv("ADMIN_USER_MODEL")

    # This value is the username field for User db/orm model for for authentication.
    ADMIN_USER_MODEL_USERNAME_FIELD: str = os.getenv("ADMIN_USER_MODEL_USERNAME_FIELD")

    # This value is the key to securing signed data - it is vital you keep this secure,
    # or attackers could use it to generate their own signed values.
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY")


settings = Settings()
