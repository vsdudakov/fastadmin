from uuid import uuid4

import pytest

from fastadmin import ModelAdmin
from fastadmin.api.schemas import ExportFormat
from fastadmin.models.base import BaseModelAdmin, DashboardWidgetAdmin
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType


async def test_not_implemented_methods():
    class Model:
        pass

    base = ModelAdmin(Model)
    with pytest.raises(NotImplementedError):
        await base.authenticate("username", "password")

    with pytest.raises(NotImplementedError):
        await base.orm_save_obj(None, {})

    with pytest.raises(NotImplementedError):
        await base.orm_delete_obj({})

    with pytest.raises(NotImplementedError):
        await base.orm_get_list()

    with pytest.raises(NotImplementedError):
        await base.orm_get_obj(0)

    with pytest.raises(NotImplementedError):
        await base.orm_get_m2m_ids({}, "test")

    with pytest.raises(NotImplementedError):
        await base.orm_save_m2m_ids({}, "test", [])

    with pytest.raises(NotImplementedError):
        await base.get_model_fields_with_widget_types()

    with pytest.raises(NotImplementedError):
        await base.get_model_pk_name(base.model_cls)

    with pytest.raises(NotImplementedError):
        await base.change_password(1, "secret")

    with pytest.raises(NotImplementedError):
        await base.orm_save_upload_field({}, "file", "base64")

    with pytest.raises(NotImplementedError):
        await DashboardWidgetAdmin().get_data()


async def test_export_wrong_format(mocker):
    class Model:
        pass

    base = ModelAdmin(Model)

    mocker.patch.object(base, "get_model_fields_with_widget_types", return_value=[])
    assert not base.get_fields_for_serialize()

    values = [
        ModelFieldWidgetSchema(
            name=f"test_{index}",
            column_name=f"test_{index}",
            is_m2m=False,
            is_pk=False,
            is_immutable=False,
            form_widget_type=WidgetType.Input,
            form_widget_props={},
            filter_widget_type=WidgetType.Input,
            filter_widget_props={},
        )
        for index in range(3)
    ]
    mocker.patch.object(base, "get_model_fields_with_widget_types", return_value=values)
    fields = base.get_fields_for_serialize()
    assert len(fields) == 3
    assert "test_0" in base.get_fields_for_serialize()

    base.exclude = ("test_0",)
    fields = base.get_fields_for_serialize()
    assert len(fields) == 2
    assert "test_0" not in base.get_fields_for_serialize()

    base.fields = ("test_0",)
    base.exclude = ("test_0",)
    fields = base.get_fields_for_serialize()
    assert len(fields) == 0
    assert "test_0" not in base.get_fields_for_serialize()

    base.fields = ("test_0",)
    base.exclude = ()
    fields = base.get_fields_for_serialize()
    assert len(fields) == 1
    assert "test_0" in base.get_fields_for_serialize()

    base.fields = ("test_0",)
    base.list_display = ("test_1",)
    base.exclude = ()
    fields = base.get_fields_for_serialize()
    assert len(fields) == 2
    assert "test_0" in base.get_fields_for_serialize()
    assert "test_1" in base.get_fields_for_serialize()


def test_resolve_sort_by_regular_field():
    """resolve_sort_by returns sort_by unchanged for non-display fields."""
    from fastadmin import ModelAdmin

    class Model:
        pass

    class Admin(ModelAdmin):
        pass

    admin = Admin(Model)
    assert admin.resolve_sort_by("name") == "name"
    assert admin.resolve_sort_by("-created_at") == "-created_at"
    assert admin.resolve_sort_by("") == ""


def test_resolve_sort_by_display_with_sorter_string():
    """resolve_sort_by returns the sorter string for @display(sorter='expr') columns."""
    from fastadmin import ModelAdmin, display

    class Model:
        pass

    class Admin(ModelAdmin):
        @display(sorter="user__username")
        def author(self, obj):
            return (getattr(obj, "user", None) and getattr(obj.user, "username", "")) or ""

    admin = Admin(Model)
    assert admin.resolve_sort_by("author") == "user__username"
    assert admin.resolve_sort_by("-author") == "-user__username"


def test_resolve_sort_by_display_with_sorter_true():
    """resolve_sort_by returns sort_by as-is when display has sorter=True (use function name)."""
    from fastadmin import ModelAdmin, display

    class Model:
        pass

    class Admin(ModelAdmin):
        @display(sorter=True)
        def user__username(self, obj):
            return (getattr(obj, "user", None) and getattr(obj.user, "username", "")) or ""

    admin = Admin(Model)
    assert admin.resolve_sort_by("user__username") == "user__username"
    assert admin.resolve_sort_by("-user__username") == "-user__username"


async def test_get_fields_for_serialize(mocker):
    class Model:
        pass

    base = ModelAdmin(Model)

    mocker.patch.object(base, "orm_get_list", return_value=([], 0))
    mocker.patch.object(base, "get_model_fields_with_widget_types", return_value=[])
    assert await base.get_export("wrong_format") is None


async def test_base_model_admin_serialize_obj_by_id_none_and_value():
    class Model:
        pass

    base = ModelAdmin(Model)

    async def orm_get_obj_none(_id):
        return None

    base.orm_get_obj = orm_get_obj_none  # type: ignore[method-assign]
    assert await base.orm_serialize_obj_by_id(1) is None

    async def orm_get_obj(_id):
        return {"id": _id}

    async def serialize_obj(_obj):
        return {"id": 1}

    base.orm_get_obj = orm_get_obj  # type: ignore[method-assign]
    base.serialize_obj = serialize_obj  # type: ignore[method-assign]
    assert await base.orm_serialize_obj_by_id(1) == {"id": 1}


async def test_serialize_obj_attributes_with_async_str():
    class AsyncStrObj:
        value = 7

        async def __str__(self):  # type: ignore[override]
            return "async-obj"

    class Model:
        pass

    base = ModelAdmin(Model)
    fields = [
        ModelFieldWidgetSchema(
            name="value",
            column_name="value",
            is_m2m=False,
            is_pk=False,
            is_immutable=False,
            form_widget_type=WidgetType.Input,
            form_widget_props={},
            filter_widget_type=WidgetType.Input,
            filter_widget_props={},
        )
    ]
    result = await base.serialize_obj_attributes(AsyncStrObj(), fields)
    assert result["value"] == 7
    assert result["__str__"] == "async-obj"


async def test_serialize_obj_after_save_detached_paths():
    class Model:
        pass

    class DetachedInstanceError(Exception):
        pass

    base = ModelAdmin(Model)
    obj = type("Obj", (), {"id": 10})()

    async def raise_non_detached(_obj):
        raise RuntimeError("boom")

    base.serialize_obj = raise_non_detached  # type: ignore[method-assign]
    with pytest.raises(RuntimeError):
        await base._serialize_obj_after_save(obj)

    async def raise_detached(_obj):
        raise DetachedInstanceError("detached")

    base.serialize_obj = raise_detached  # type: ignore[method-assign]
    base.get_model_pk_name = lambda _cls: "id"  # type: ignore[method-assign]

    obj_without_pk = type("Obj", (), {"id": None})()
    with pytest.raises(DetachedInstanceError):
        await base._serialize_obj_after_save(obj_without_pk)

    async def serialize_by_id_none(_id):
        return None

    base.orm_serialize_obj_by_id = serialize_by_id_none  # type: ignore[method-assign]
    with pytest.raises(DetachedInstanceError):
        await base._serialize_obj_after_save(obj)

    async def serialize_by_id_ok(_id):
        return {"id": _id}

    base.orm_serialize_obj_by_id = serialize_by_id_ok  # type: ignore[method-assign]
    assert await base._serialize_obj_after_save(obj) == {"id": 10}


async def test_serialize_obj_skips_non_serialized_fields():
    class Obj:
        name = "n"
        hidden = "h"

        def __str__(self):
            return "obj"

    class Model:
        pass

    base = ModelAdmin(Model)
    fields = [
        ModelFieldWidgetSchema(
            name="name",
            column_name="name",
            is_m2m=False,
            is_pk=False,
            is_immutable=False,
            form_widget_type=WidgetType.Input,
            form_widget_props={},
            filter_widget_type=WidgetType.Input,
            filter_widget_props={},
        ),
        ModelFieldWidgetSchema(
            name="hidden",
            column_name="hidden",
            is_m2m=False,
            is_pk=False,
            is_immutable=False,
            form_widget_type=WidgetType.Input,
            form_widget_props={},
            filter_widget_type=WidgetType.Input,
            filter_widget_props={},
        ),
    ]
    base.get_model_fields_with_widget_types = lambda *args, **kwargs: fields  # type: ignore[method-assign]
    base.get_fields_for_serialize = lambda: {"name"}  # type: ignore[method-assign]
    result = await base.serialize_obj(Obj())
    assert "name" in result
    assert "hidden" not in result


def test_deserialize_value_timepicker_fallback_and_datetime():
    field_time = ModelFieldWidgetSchema(
        name="t",
        column_name="t",
        is_m2m=False,
        is_pk=False,
        is_immutable=False,
        form_widget_type=WidgetType.TimePicker,
        form_widget_props={},
        filter_widget_type=WidgetType.Input,
        filter_widget_props={},
    )
    field_dt = ModelFieldWidgetSchema(
        name="dt",
        column_name="dt",
        is_m2m=False,
        is_pk=False,
        is_immutable=False,
        form_widget_type=WidgetType.DateTimePicker,
        form_widget_props={},
        filter_widget_type=WidgetType.Input,
        filter_widget_props={},
    )
    base = ModelAdmin(type("Model", (), {}))
    assert base.deserialize_value(field_time, "12:34:56").isoformat() == "12:34:56"
    assert base.deserialize_value(field_dt, "2026-02-19T12:34:56").isoformat() == "2026-02-19T12:34:56"


async def test_save_model_sync_upload_and_model_admin_password_flow():
    class DummyAdmin(ModelAdmin):
        @staticmethod
        def get_model_pk_name(_orm_model_cls):
            return "id"

        def get_model_fields_with_widget_types(self, with_m2m=None, with_upload=None):
            if with_upload:
                return [
                    ModelFieldWidgetSchema(
                        name="avatar",
                        column_name="avatar",
                        is_m2m=False,
                        is_pk=False,
                        is_immutable=False,
                        form_widget_type=WidgetType.Upload,
                        form_widget_props={},
                        filter_widget_type=WidgetType.Input,
                        filter_widget_props={},
                    )
                ]
            if with_m2m:
                return []
            return [
                ModelFieldWidgetSchema(
                    name="password",
                    column_name="password",
                    is_m2m=False,
                    is_pk=False,
                    is_immutable=False,
                    form_widget_type=WidgetType.PasswordInput,
                    form_widget_props={},
                    filter_widget_type=WidgetType.Input,
                    filter_widget_props={},
                )
            ]

        async def orm_save_obj(self, _id, payload):
            assert payload["password"] == "raw"
            return {"id": 42, **payload}

        async def orm_get_obj(self, _id):
            return None

        async def orm_get_list(self, **kwargs):
            return [], 0

        async def orm_delete_obj(self, _id):
            return None

        async def orm_get_m2m_ids(self, _obj, _field):
            return []

        async def orm_save_m2m_ids(self, _obj, _field, _ids):
            return None

        def orm_save_upload_field(self, obj, field, base64):
            obj[field] = base64

        async def change_password(self, id, password):
            self.changed = (id, password)

    admin = DummyAdmin(type("Model", (), {}))

    async def passthrough(obj):
        return obj

    admin._serialize_obj_after_save = passthrough  # type: ignore[method-assign]
    payload = {"password": "raw", "avatar": "base64-image"}
    result = await admin.save_model(None, payload)
    assert result is not None
    assert result["avatar"] == "base64-image"
    assert admin.changed == (42, "raw")


async def test_save_model_async_upload_field_branch():
    class DummyAdmin(ModelAdmin):
        @staticmethod
        def get_model_pk_name(_orm_model_cls):
            return "id"

        def get_model_fields_with_widget_types(self, with_m2m=None, with_upload=None):
            if with_upload:
                return [
                    ModelFieldWidgetSchema(
                        name="avatar",
                        column_name="avatar",
                        is_m2m=False,
                        is_pk=False,
                        is_immutable=False,
                        form_widget_type=WidgetType.Upload,
                        form_widget_props={},
                        filter_widget_type=WidgetType.Input,
                        filter_widget_props={},
                    )
                ]
            return []

        async def orm_save_obj(self, _id, payload):
            return {"id": 1, **payload}

        async def orm_get_obj(self, _id):
            return None

        async def orm_get_list(self, **kwargs):
            return [], 0

        async def orm_delete_obj(self, _id):
            return None

        async def orm_get_m2m_ids(self, _obj, _field):
            return []

        async def orm_save_m2m_ids(self, _obj, _field, _ids):
            return None

        async def orm_save_upload_field(self, obj, field, base64):
            obj[field] = base64

    admin = DummyAdmin(type("Model", (), {}))

    async def passthrough(obj):
        return obj

    admin._serialize_obj_after_save = passthrough  # type: ignore[method-assign]
    result = await admin.save_model(None, {"avatar": "img"})
    assert result is not None
    assert result["avatar"] == "img"


async def test_get_export_json_uses_custom_encoder():
    class ExportAdmin(BaseModelAdmin):
        @staticmethod
        def get_model_pk_name(_orm_model_cls):
            return "id"

        def get_model_fields_with_widget_types(self, with_m2m=None, with_upload=None):
            return [
                ModelFieldWidgetSchema(
                    name="id",
                    column_name="id",
                    is_m2m=False,
                    is_pk=True,
                    is_immutable=False,
                    form_widget_type=WidgetType.Input,
                    form_widget_props={},
                    filter_widget_type=WidgetType.Input,
                    filter_widget_props={},
                )
            ]

        async def orm_get_list(self, **kwargs):
            return [type("Obj", (), {"id": uuid4(), "__str__": lambda self: "x"})()], 1

        async def orm_get_obj(self, _id):
            return None

        async def orm_save_obj(self, _id, payload):
            return payload

        async def orm_delete_obj(self, _id):
            return None

        async def orm_get_m2m_ids(self, _obj, _field):
            return []

        async def orm_save_m2m_ids(self, _obj, _field, _ids):
            return None

    admin = ExportAdmin(type("Model", (), {}))
    stream = await admin.get_export(ExportFormat.JSON)
    assert stream is not None
    content = stream.getvalue()
    assert '"id":' in content
