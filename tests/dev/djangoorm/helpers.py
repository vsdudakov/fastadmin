import django


def init_engine():
    django.setup(set_prefix=False)


def get_connection(engine):
    return None


def dispose_engine(engine):
    pass
