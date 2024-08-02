import logging
from pathlib import Path

logging.disable(logging.WARNING)

ROOT_DIR = Path(__file__).parent

DB_SQLITE = str(ROOT_DIR / "environment" / "db.sqlite3")


FRAMEWORKS = [
    "fastapi",
    "flask",
    "django",
]

ORMS = [
    "tortoiseorm",
    "djangoorm",
    "sqlalchemy",
    # TODO: fix pony orm
    # "ponyorm",
]
