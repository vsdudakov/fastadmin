import os
from pathlib import Path

from pydantic import BaseSettings, Field

SETTINGS_ENV_FILE: str = os.getenv("ADMIN_ENV_FILE") or ".env"

ROOT_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Settings"""

    USER_MODEL: str = Field(
        description="The name for User db/orm model class for authentication."
    )

    USER_MODEL_USERNAME_FIELD: str = Field(
        description="The username field for User db/orm model for authentication."
    )

    SECRET_KEY: str = Field(
        description=(
            "The key to securing signed data - it is vital you keep this secure,"
            "or attackers could use it to generate their own signed values."
        )
    )

    PREFIX: str = Field(
        default="admin",
        description="The prefix you used for mounting FastAdmin app for FastAPI.",
    )

    SITE_NAME: str = Field(
        default="FastAdmin",
        description="The site name on sign-in page and on header.",
    )

    SITE_SIGN_IN_LOGO: str = Field(
        default="/admin/static/images/sign-in-logo.svg",
        description="The logo path on sign-in page.",
    )

    SITE_HEADER_LOGO: str = Field(
        default="/admin/static/images/header-logo.svg",
        description="The logo path on header.",
    )

    SITE_FAVICON: str = Field(
        default="/admin/static/images/favicon.png",
        description="The favicon path.",
    )

    PRIMARY_COLOR: str = Field(
        default="#009485",
        description="The primary color for FastAdmin.",
    )

    SESSION_ID_KEY: str = Field(
        default="admin_session_id",
        description="The session id key to store session id in http only cookies.",
    )

    SESSION_EXPIRED_AT: int = Field(
        default=144000,  # in sec
        description="The expired_at period (in sec) for session id.",
    )

    DATE_FORMAT: str = Field(
        default="YYYY-MM-DD",
        description="The date format for JS widgets.",
    )

    DATETIME_FORMAT: str = Field(
        default="YYYY-MM-DD HH:mm",
        description="The datetime format for JS widgets.",
    )

    TIME_FORMAT: str = Field(
        default="HH:mm:ss",
        description="The time format for JS widgets.",
    )

    class Config(BaseSettings.Config):
        env_file = SETTINGS_ENV_FILE
        env_file_encoding = "utf-8"
        env_prefix = "ADMIN_"


settings = Settings()
