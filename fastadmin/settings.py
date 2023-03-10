import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv(os.getenv("ADMIN_ENV_FILE") or ".env")


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    """Settings"""

    # This value is the prefix you used for mounting FastAdmin app for FastAPI.
    ADMIN_PREFIX: str = "admin"

    # This value is the site name on sign-in page and on header.
    ADMIN_SITE_NAME: str = "FastAdmin"

    # This value is the logo path on sign-in page.
    ADMIN_SITE_SIGN_IN_LOGO: str = "/admin/static/images/sign-in-logo.svg"

    # This value is the logo path on header.
    ADMIN_SITE_HEADER_LOGO: str = "/admin/static/images/header-logo.svg"

    # This value is the favicon path.
    ADMIN_SITE_FAVICON: str = "/admin/static/images/favicon.png"

    # This value is the primary color for FastAdmin.
    ADMIN_PRIMARY_COLOR: str = "#009485"

    # This value is the session id key to store session id in http only cookies.
    ADMIN_SESSION_ID_KEY: str = "admin_session_id"

    # This value is the expired_at period (in sec) for session id.
    ADMIN_SESSION_EXPIRED_AT: int = 144000  # in sec

    # This value is the name for User db/orm model class for authentication.
    ADMIN_USER_MODEL: str

    # This value is the username field for User db/orm model for for authentication.
    ADMIN_USER_MODEL_USERNAME_FIELD: str

    # This value is the key to securing signed data - it is vital you keep this secure,
    # or attackers could use it to generate their own signed values.
    ADMIN_SECRET_KEY: str

    # This value is the date format for JS widgets.
    ADMIN_DATE_FORMAT: str = "YYYY-MM-DD"

    # This value is the datetime format for JS widgets.
    ADMIN_DATETIME_FORMAT: str = "YYYY-MM-DD HH:mm"

    # This value is the time format for JS widgets.
    ADMIN_TIME_FORMAT: str = "HH:mm:ss"


settings = Settings()  # type: ignore
