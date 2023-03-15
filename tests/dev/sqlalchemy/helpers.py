from .models import sqlalchemy_engine, sqlalchemy_sessionmaker


def init_connection():
    pass


def get_connection():
    return sqlalchemy_sessionmaker


async def close_connection():
    await sqlalchemy_engine.dispose()
