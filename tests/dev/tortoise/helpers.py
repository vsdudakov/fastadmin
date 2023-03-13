from tortoise import Tortoise

from tests.settings import DB_SQLITE


async def init_connection():
    await Tortoise.init(db_url=f"sqlite://{DB_SQLITE}", modules={"models": ["tests.dev.tortoise.models"]})
    await Tortoise.generate_schemas()


async def close_connection():
    await Tortoise.close_connections()
