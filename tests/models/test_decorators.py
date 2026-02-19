import pytest

from fastadmin import ModelAdmin, display, register
from fastadmin.models.base import DashboardWidgetAdmin
from fastadmin.models.decorators import register_widget
from fastadmin.models.schemas import DashboardWidgetType


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


def test_register_widget_error():
    class InvalidWidget:
        pass

    with pytest.raises(ValueError, match="Wrapped class must subclass DashboardWidgetAdmin."):
        register_widget(InvalidWidget)


def test_register_widget_success():
    from fastadmin.models.base import admin_dashboard_widgets

    class MyWidget(DashboardWidgetAdmin):
        title = "MyWidget"
        dashboard_widget_type = DashboardWidgetType.ChartLine
        x_field = "x"

    prev = admin_dashboard_widgets.copy()
    try:
        returned = register_widget(MyWidget)
        assert returned is MyWidget
        assert "MyWidget" in admin_dashboard_widgets
    finally:
        admin_dashboard_widgets.clear()
        admin_dashboard_widgets.update(prev)
