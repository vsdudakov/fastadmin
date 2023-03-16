import logging
import os

logging.disable(logging.WARNING)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_SQLITE = os.path.join(ROOT_DIR, "..", "examples", "db.sqlite3")


FRAMEWORKS = [
    "fastapi",
    "flask",
    "django",
]

ORMS = [
    "tortoiseorm",
    "djangoorm",
    "sqlalchemy",
    "ponyorm",
]
