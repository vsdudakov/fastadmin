import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv(os.getenv("ADMIN_ENV_FILE") or ".env")


class Settings(BaseSettings):
    """Settings"""

    ADMIN_PREFIX: str = "admin"

    ADMIN_SITE_NAME: str = "FastAdmin"
    ADMIN_SITE_SIGN_IN_LOGO: str = "/admin/static/images/sign-in-logo.svg"
    ADMIN_SITE_HEADER_LOGO: str = "/admin/static/images/header-logo.svg"
    ADMIN_SITE_FAVICON: str = "/admin/static/images/favicon.png"
    ADMIN_PRIMARY_COLOR: str = "#009485"

    ADMIN_SESSION_ID_KEY: str = "admin_session_id"
    ADMIN_SESSION_EXPIRED_AT: int = 144000  # in sec
    ADMIN_USER_MODEL: str
    ADMIN_USER_MODEL_USERNAME_FIELD: str
    ADMIN_SECRET_KEY: str

    ADMIN_DATE_FORMAT: str = "YYYY-MM-DD"
    ADMIN_DATETIME_FORMAT: str = "YYYY-MM-DD HH:mm"
    ADMIN_TIME_FORMAT: str = "HH:mm:ss"


settings = Settings()
