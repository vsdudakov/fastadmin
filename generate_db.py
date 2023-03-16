import asyncio
import os

from tortoise import Tortoise

from tests.settings import DB_SQLITE


async def generate_db():
    if os.path.exists(DB_SQLITE):
        os.remove(DB_SQLITE)
    await Tortoise.init(db_url=f"sqlite://{DB_SQLITE}", modules={"models": ["examples.tortoiseorm.models"]})
    # Tortoise ORM generates sqlite file for all ORMs
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


asyncio.run(generate_db())
