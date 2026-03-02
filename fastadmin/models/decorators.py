import typing as tp

from fastadmin.models.schemas import (
    WidgetActionChartProps,
    WidgetActionFilter,
    WidgetActionProps,
    WidgetActionType,
)


def action(
    function=None,
    *,
    description: str | None = None,
):
    """Conveniently add attributes to an action function:

    Example of usage:
    @action(
        description="Mark selected stories as published",
    )
    async def make_published(self, objs: list[Any]) -> ActionResponseSchema | None:
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
    return decorator(function)


def widget_action(
    function=None,
    *,
    tab: str = "Default",
    title: str = "Action",
    description: str | None = None,
    widget_action_type: WidgetActionType = WidgetActionType.Action,
    widget_action_props: WidgetActionChartProps | WidgetActionProps | None = None,
    widget_action_filters: list[WidgetActionFilter] | None = None,
    width: (
        tp.Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24] | None
    ) = None,  # width in 1-24 grid system
):
    """Conveniently add attributes to a widget action function:

    Example of usage:
    @widget_action(
        tab="Default",
        title="Action",
        description="Chart of total sales by status",
        widget_action_type=WidgetActionType.Action,
        widget_action_props=WidgetActionChartProps(
            x_field="date",
            y_field="total_sales",
            series_field="status",
        ),
        widget_action_filters=[WidgetActionFilter(
            field_name="status",
            widget_type=WidgetType.Select,
            widget_props={
                "mode": "multiple",
                "options": [
                    {
                        "label": "Pending",
                        "value": "Pending",
                    },
                    {
                        "label": "Completed",
                        "value": "Completed",
                    },
                ],
            },
        )],
    )
    async def sales_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        # filter by payload.query
        return WidgetActionResponseSchema(
            data=[
                {
                    "date": "2026-01-01",
                    "total_sales": 100,
                    "status": "Pending",
                },
                {
                    "date": "2026-01-02",
                    "total_sales": 200,
                    "status": "Completed",
                },
            ],
        )

    :param function: A function to decorate.
    :param description: A string value to set the function's short_description
    """

    def decorator(func):
        func.is_widget_action = True
        func.widget_action_type = widget_action_type
        func.widget_action_props = widget_action_props
        func.widget_action_filters = widget_action_filters
        func.tab = tab
        func.title = title
        func.width = width
        if description is not None:
            func.short_description = description
        return func

    if function is None:
        return decorator
    return decorator(function)


def display(function=None, *, sorter: bool | str = False):
    """Conveniently add attributes to a display function:

    Example of usage:
    @display
    async def is_published(self, obj):
        return obj.publish_date is not None

    @display(sorter="user__username")
    async def author(self, obj):
        return obj.user.username

    :param function: A function to decorate.
    :param sorter: Enable sorting (True), use function name as sort key; or a string to specify
        the sort expression (e.g. "user__username"). **WARNING**: supported only for Django and Tortoise.
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
