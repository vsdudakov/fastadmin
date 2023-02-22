import os

from environs import Env

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = Env()

ENV_FILE = env.str("ENV_FILE", default=".env")
env.read_env(os.path.join(BASE_DIR, ENV_FILE))


class Settings:
    ADMIN_PREFIX = env.str("ADMIN_PREFIX", "admin")
    ADMIN_SESSION_ID_KEY = env.str("ADMIN_SESSION_ID_KEY", "admin_session_id")
    ADMIN_SITE_NAME = env.str("ADMIN_SITE_NAME", "API Administration")
    ADMIN_SITE_SIGN_IN_LOGO = env.str(
        "ADMIN_SITE_SIGN_IN_LOGO",
        "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
    )
    ADMIN_SITE_HEADER_LOGO = env.str(
        "ADMIN_SITE_HEADER_LOGO", "https://fastapi.tiangolo.com/img/icon-white.svg"
    )
    ADMIN_SITE_FAVICON = env.str(
        "ADMIN_SITE_FAVICON", "https://fastapi.tiangolo.com/img/favicon.png"
    )
    ADMIN_PRIMARY_COLOR = env.str("ADMIN_PRIMARY_COLOR", "#009485")


settings = Settings()
