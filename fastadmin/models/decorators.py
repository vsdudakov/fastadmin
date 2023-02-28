def register(*models):
    from fastadmin.models.base import BaseModelAdmin
    from fastadmin.models.helpers import register_admin_model

    def wrapper(admin_class):
        if not models:
            raise ValueError("At least one model must be passed to register.")

        if not issubclass(admin_class, BaseModelAdmin):
            raise ValueError("Wrapped class must subclass ModelAdmin.")

        register_admin_model(admin_class, models)

        return admin_class

    return wrapper
