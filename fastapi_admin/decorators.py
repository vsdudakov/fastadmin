def register(*models):
    from models import ModelAdmin, register_admin_model

    def wrapper(admin_class):
        if not models:
            raise ValueError("At least one model must be passed to register.")

        if not issubclass(admin_class, ModelAdmin):
            raise ValueError("Wrapped class must subclass ModelAdmin.")

        register_admin_model(admin_class, models)

        return admin_class

    return wrapper
