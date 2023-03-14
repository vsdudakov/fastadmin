from tortoise import Tortoise

from tests.settings import DB_SQLITE


async def init_engine():
    await Tortoise.init(db_url=f"sqlite://{DB_SQLITE}", modules={"models": ["tests.dev.tortoise.models"]})
    await Tortoise.generate_schemas()


def get_connection(engine):
    return Tortoise.get_connection("default")


async def dispose_engine(engine):
    await Tortoise.close_connections()
