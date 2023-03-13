import django


def init_connection():
    django.setup(set_prefix=False)


def close_connection():
    pass
