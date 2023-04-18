from django.apps import AppConfig


class OrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tests.environment.djangoorm"
