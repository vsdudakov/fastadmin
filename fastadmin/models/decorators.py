def register(*models):
    """Register a model with the admin model.

    :param models: A list of models to register.
    """
    from fastadmin.models.base import BaseModelAdmin
    from fastadmin.models.helpers import register_admin_model

    def wrapper(admin_class):
        """Wrapper for register.

        :param admin_class: A class to wrap.
        """
        if not models:
            raise ValueError("At least one model must be passed to register.")

        if not issubclass(admin_class, BaseModelAdmin):
            raise ValueError("Wrapped class must subclass ModelAdmin.")

        register_admin_model(admin_class, models)

        return admin_class

    return wrapper
