import pytest

from fastadmin import ModelAdmin
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
