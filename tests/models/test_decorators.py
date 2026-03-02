import pytest

from fastadmin import ModelAdmin, display, register
from fastadmin.models.decorators import action, widget_action
from fastadmin.models.schemas import WidgetActionChartProps, WidgetActionType


def test_display_sorter_string():
    """@display(sorter='expr') sets sorter to the given string."""

    @display(sorter="user__username")
    def author(self, obj):
        return str(obj)

    assert author.is_display is True
    assert author.sorter == "user__username"


def test_display_sorter_true():
    """@display(sorter=True) sets sorter to True."""

    @display(sorter=True)
    def user__username(self, obj):
        return str(obj)

    assert user__username.is_display is True
    assert user__username.sorter is True


async def test_register():
    class Model:
        pass

    class MyModelAdmin(ModelAdmin):
        pass

    assert register(Model)(MyModelAdmin)


async def test_register_error():
    class Model:
        pass

    class InvalidModelAdmin:
        pass

    class MyModelAdmin(ModelAdmin):
        pass

    with pytest.raises(ValueError, match="At least one model must be passed to register."):
        register()(MyModelAdmin)

    with pytest.raises(ValueError, match="Wrapped class must subclass ModelAdmin."):
        register(Model)(InvalidModelAdmin)


def test_action_decorator_sets_metadata():
    """@action sets is_action flag and optional short_description."""

    @action(description="Do something")
    async def do_something(objs):
        return None

    assert getattr(do_something, "is_action", False) is True
    assert getattr(do_something, "short_description", "") == "Do something"


def test_widget_action_decorator_defaults():
    """@widget_action without explicit kwargs uses documented defaults."""

    @widget_action()
    async def default_widget(payload):
        return None

    assert getattr(default_widget, "is_widget_action", False) is True
    assert default_widget.widget_action_type is WidgetActionType.Action
    assert default_widget.widget_action_props is None
    assert default_widget.tab == "Default"
    assert default_widget.title == "Action"
    # No description passed -> no short_description attribute
    assert not hasattr(default_widget, "short_description")


def test_widget_action_decorator_with_chart_props():
    """@widget_action attaches chart props and metadata."""

    props = WidgetActionChartProps(x_field="created_at", y_field="total", series_field="status")

    @widget_action(
        widget_action_type=WidgetActionType.ChartLine,
        widget_action_props=props,
        tab="Analytics",
        title="Sales over time",
        description="Line chart of sales",
    )
    async def sales_chart(payload):
        return None

    assert getattr(sales_chart, "is_widget_action", False) is True
    assert sales_chart.widget_action_type is WidgetActionType.ChartLine
    assert sales_chart.widget_action_props is props
    assert sales_chart.tab == "Analytics"
    assert sales_chart.title == "Sales over time"
    assert getattr(sales_chart, "short_description", "") == "Line chart of sales"


def test_widget_action_used_without_parentheses():
    """@widget_action used without parentheses still sets metadata."""

    @widget_action
    async def simple_action(payload):
        return None

    assert getattr(simple_action, "is_widget_action", False) is True
    # Defaults are preserved
    assert simple_action.widget_action_type is WidgetActionType.Action
    assert simple_action.widget_action_props is None
