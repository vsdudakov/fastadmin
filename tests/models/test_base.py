import pytest

from fastadmin import ModelAdmin
from fastadmin.models.schemas import WidgetType


async def test_not_implemented_methods():
    class Model:
        pass

    base = ModelAdmin(Model)
    with pytest.raises(NotImplementedError):
        await base.authenticate("username", "password")

    with pytest.raises(NotImplementedError):
        await base.save_model(0, {})

    with pytest.raises(NotImplementedError):
        await base.delete_model(0)

    with pytest.raises(NotImplementedError):
        await base.get_obj(0)

    with pytest.raises(NotImplementedError):
        await base.get_list()

    with pytest.raises(NotImplementedError):
        base.get_model_fields()

    with pytest.raises(NotImplementedError):
        base.get_form_widget("test")


async def test_export_wrong_format(mocker):
    class Model:
        pass

    base = ModelAdmin(Model)

    mocker.patch.object(base, "get_list", return_value=([], 0))
    mocker.patch.object(base, "get_model_fields", return_value={})
    await base.get_export("wrong_format") is None


async def test_get_filter_widget(mocker):
    class Model:
        pass

    base = ModelAdmin(Model)
    mocker.patch.object(base, "get_form_widget", return_value=(WidgetType.AsyncTransfer, {}))
    widget_type, widget_props = base.get_filter_widget("test")
    assert widget_type == WidgetType.AsyncTransfer
    assert not widget_props["required"]

    mocker.patch.object(base, "get_form_widget", return_value=(WidgetType.Checkbox, {}))
    widget_type, widget_props = base.get_filter_widget("test")
    assert widget_type == WidgetType.RadioGroup
    assert not widget_props["required"]
    assert widget_props["options"] == [
        {"label": "Yes", "value": True},
        {"label": "No", "value": False},
    ]

    mocker.patch.object(base, "get_form_widget", return_value=(WidgetType.CheckboxGroup, {}))
    widget_type, widget_props = base.get_filter_widget("test")
    assert widget_type == WidgetType.CheckboxGroup
    assert not widget_props["required"]

    mocker.patch.object(base, "get_form_widget", return_value=("Invalid", {}))
    widget_type, widget_props = base.get_filter_widget("test")
    assert widget_type == WidgetType.Input
    assert not widget_props["required"]
