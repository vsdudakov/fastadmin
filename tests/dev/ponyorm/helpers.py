from pony.orm import db_session


def init_connection():
    pass


def get_connection():
    return db_session


def close_connection():
    pass
