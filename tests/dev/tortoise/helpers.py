from tortoise import Tortoise

from tests.settings import DB_SQLITE


async def init_connection():
    await Tortoise.init(db_url=f"sqlite://{DB_SQLITE}", modules={"models": ["tests.dev.tortoise.models"]})
    # Tortise ORM generates sqlite file for all ORMs
    await Tortoise.generate_schemas()


def get_connection():
    return Tortoise.get_connection("default")


async def close_connection():
    await Tortoise.close_connections()
