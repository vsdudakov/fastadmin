import logging
from pathlib import Path

logging.disable(logging.WARNING)

ROOT_DIR = Path(__file__).parent

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
