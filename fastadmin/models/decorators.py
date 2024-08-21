def action(function=None, *, description: str | None = None):
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


# TODO: make the sorter parameter a string to specify how to sort the data
def display(function=None, *, sorter: bool = False):
    """Conveniently add attributes to a display function:

    Example of usage:
    @display
    async def is_published(self, obj):
        return obj.publish_date is not None

    :param function: A function to decorate.
    :param sorter: Enable sorting or not. **WARNING**: supported only for Django and Tortoise.
        Function name should be like an ORM ordering param, e.g. `def user__username(self, obj)`.
    """

    def decorator(func):
        func.is_display = True
        func.sorter = sorter
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

    def wrapper(model_admin_cls):
        """Wrapper for register.

        :param model_admin_cls: A class to wrap.
        """
        if not orm_model_classes:
            raise ValueError("At least one model must be passed to register.")

        if not issubclass(model_admin_cls, ModelAdmin):
            raise ValueError("Wrapped class must subclass ModelAdmin.")

        register_admin_model_class(model_admin_cls, orm_model_classes, **kwargs)

        return model_admin_cls

    return wrapper


def register_widget(dashboard_widget_admin_cls):
    """Wrapper for register dashboard widget.

    :param admin_class: A class to wrap.
    """
    from fastadmin.models.base import DashboardWidgetAdmin, admin_dashboard_widgets

    if not issubclass(dashboard_widget_admin_cls, DashboardWidgetAdmin):
        raise ValueError("Wrapped class must subclass DashboardWidgetAdmin.")

    admin_dashboard_widgets[dashboard_widget_admin_cls.__name__] = dashboard_widget_admin_cls()

    return dashboard_widget_admin_cls
