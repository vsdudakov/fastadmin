from asgiref.sync import sync_to_async  # noqa: F401


def action(function=None, *, description: str = None):
    """Conveniently add attributes to an action function:

    Example of usage:
    @action(
        description="Mark selected stories as published",
    )
    async def make_published(self, objs: list[Any]) -> None:
        ...

    :param function: A function to decorate.
    :param description: A string value to set the function's short_description
    """

    def decorator(func):
        func.is_action = True
        if description is not None:
            func.short_description = description
        return func

    if function is None:
        return decorator
    else:
        return decorator(function)


def display(function=None):
    """Conveniently add attributes to a display function:

    Example of usage:
    @display
    async def is_published(self, obj):
        return obj.publish_date is not None

    :param function: A function to decorate.
    """

    def decorator(func):
        func.is_display = True
        return func

    if function is None:
        return decorator
    else:
        return decorator(function)


def register(*orm_model_classes, **kwargs):
    """Register the given model(s) classes and wrapped ModelAdmin class with
    admin site:

    Example of usage:
    @register(Author)
    class AuthorAdmin(admin.ModelAdmin):
        pass

    :param models: A list of models to register.
    """
    from fastadmin.models.base import ModelAdmin
    from fastadmin.models.helpers import register_admin_model_class

    def wrapper(admin_model_class):
        """Wrapper for register.

        :param admin_class: A class to wrap.
        """
        if not orm_model_classes:
            raise ValueError("At least one model must be passed to register.")

        if not issubclass(admin_model_class, ModelAdmin):
            raise ValueError("Wrapped class must subclass ModelAdmin.")

        register_admin_model_class(admin_model_class, orm_model_classes, **kwargs)

        return admin_model_class

    return wrapper
