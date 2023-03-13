from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tests.settings import DB_SQLITE


def init_engine():
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{DB_SQLITE}",
        echo=True,
    )
    return engine


def get_connection(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


async def dispose_engine(engine):
    await engine.dispose()
