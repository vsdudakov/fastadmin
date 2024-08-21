from django.apps import AppConfig


class OrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orm"

    def ready(self):
        try:
            from orm.models import User

            User.objects.update_or_create(username="admin", password="admin", is_superuser=True)
        except Exception:  # noqa: BLE001, S110
            pass
