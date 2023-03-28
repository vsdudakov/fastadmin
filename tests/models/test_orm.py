from fastadmin.models.helpers import get_admin_model
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType


def test_get_form_widget_user(user):
    admin_model_obj = get_admin_model(user.__class__)
    fields: list[ModelFieldWidgetSchema] = admin_model_obj.get_model_fields_with_widget_types()
    for field in (
        "id",
        "created_at",
        "updated_at",
        "username",
        "password",
        "is_superuser",
    ):
        assert field in [f.name for f in fields]
    for field in fields:
        match field.name:
            case "id":
                assert field.column_name == "id"
                assert not field.is_m2m
                assert field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "created_at":
                assert field.column_name == "created_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "updated_at":
                assert field.column_name == "updated_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "username":
                assert field.column_name == "username"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.Input
                assert field.form_widget_props
            case "password":
                assert field.column_name == "password"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.Input
                assert field.form_widget_props
            case "is_superuser":
                assert field.column_name == "is_superuser"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.RadioGroup
                assert field.filter_widget_props["options"]
                assert field.form_widget_type == WidgetType.Switch
                assert field.form_widget_props
            case "events":
                assert field.column_name == "events"
                assert field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props["mode"] == "multiple"
            case _:
                raise ValueError(f"Unexpected field: {field.name}")


def test_get_form_widget_tournament(tournament):
    admin_model_obj = get_admin_model(tournament.__class__)
    fields: list[ModelFieldWidgetSchema] = admin_model_obj.get_model_fields_with_widget_types()
    for field in (
        "id",
        "created_at",
        "updated_at",
        "name",
    ):
        assert field in [f.name for f in fields]
    for field in fields:
        match field.name:
            case "id":
                assert field.column_name == "id"
                assert not field.is_m2m
                assert field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "created_at":
                assert field.column_name == "created_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "updated_at":
                assert field.column_name == "updated_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "name":
                assert field.column_name == "name"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.Input
                assert field.form_widget_props
            case "events":
                assert field.column_name == "events"
                assert field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props["mode"] == "multiple"
            case _:
                raise ValueError(f"Unexpected field: {field.name}")


def test_get_form_widget_event(event):
    admin_model_obj = get_admin_model(event.__class__)
    fields: list[ModelFieldWidgetSchema] = admin_model_obj.get_model_fields_with_widget_types()
    for field in (
        "id",
        "created_at",
        "updated_at",
        "base",
        "name",
        "tournament",
        "participants",
        "is_active",
        "start_time",
        "date",
        "latitude",
        "longitude",
        "price",
        "json",
    ):
        assert field in [f.name for f in fields]
    for field in fields:
        match field.name:
            case "id":
                assert field.column_name == "id"
                assert not field.is_m2m
                assert field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "created_at":
                assert field.column_name == "created_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "updated_at":
                assert field.column_name == "updated_at"
                assert not field.is_m2m
                assert not field.is_pk
                assert field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DateTimePicker
                assert field.form_widget_props
            case "base":
                assert field.column_name in ("base_id", "base")
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props
            case "name":
                assert field.column_name == "name"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.Input
                assert field.form_widget_props
            case "tournament":
                assert field.column_name in ("tournament_id", "tournament")
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props
            case "participants":
                assert field.column_name == "participants"
                assert field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.AsyncSelect
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.AsyncSelect
                assert field.form_widget_props["mode"] == "multiple"
            case "rating":
                assert field.column_name == "rating"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "description":
                assert field.column_name == "description"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.TextArea
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.TextArea
                assert field.form_widget_props
            case "event_type":
                assert field.column_name == "event_type"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Select
                assert field.filter_widget_props["options"]
                assert field.filter_widget_props["mode"] == "multiple"
                assert field.form_widget_type == WidgetType.Select
                assert field.form_widget_props["options"]
            case "is_active":
                assert field.column_name == "is_active"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.RadioGroup
                assert field.filter_widget_props["options"]
                assert field.form_widget_type == WidgetType.Switch
                assert field.form_widget_props
            case "start_time":
                assert field.column_name == "start_time"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.TimePicker
                assert field.form_widget_props
            case "date":
                assert field.column_name == "date"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.RangePicker
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.DatePicker
                assert field.form_widget_props
            case "latitude":
                assert field.column_name == "latitude"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "longitude":
                assert field.column_name == "longitude"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "price":
                assert field.column_name == "price"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.InputNumber
                assert field.filter_widget_props
                assert field.form_widget_type == WidgetType.InputNumber
                assert field.form_widget_props
            case "json":
                assert field.column_name == "json"
                assert not field.is_m2m
                assert not field.is_pk
                assert not field.is_immutable
                assert field.filter_widget_type == WidgetType.Input
                assert field.filter_widget_props
                assert field.form_widget_type in (WidgetType.Input, WidgetType.JsonTextArea)
                assert field.form_widget_props
            case _:
                raise ValueError(f"Unexpected field: {field.name}")
