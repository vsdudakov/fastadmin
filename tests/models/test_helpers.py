import builtins
import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import ClassVar

import pytest

from fastadmin import ModelAdmin, display
from fastadmin.models.helpers import (
    generate_dashboard_widgets_schema,
    generate_models_schema,
    get_admin_model,
    get_admin_or_admin_inline_model,
    register_admin_model_class,
    unregister_admin_model_class,
)
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType


async def test_uregister_admin_model_class():
    class AdminModelClass(ModelAdmin):
        pass

    class OrmModelClass:
        pass

    register_admin_model_class(AdminModelClass, [OrmModelClass])
    assert get_admin_model(OrmModelClass.__name__)
    assert get_admin_model(OrmModelClass)
    unregister_admin_model_class([OrmModelClass])
    assert not get_admin_model(OrmModelClass.__name__)
    assert not get_admin_model(OrmModelClass)


async def test_admin_model_list_configuration_ordering(tournament, base_model_admin):
    Tournament = tournament.__class__

    class TournamentModelAdmin(base_model_admin):
        list_display = ("pseudo_name", "name", "another_calculated_field")

        @display
        def pseudo_name(self, obj: Tournament) -> str:
            return "Pseudo name"

        @display
        def another_calculated_field(self, obj: Tournament) -> int:
            return 0

    model_schema = await generate_models_schema({Tournament: TournamentModelAdmin(Tournament)})

    assert model_schema
    assert len(model_schema) == 1

    list_display = [
        (field.list_configuration.index, field.name) for field in model_schema[0].fields if field.list_configuration
    ]
    list_display.sort()
    list_display = tuple(name for index, name in list_display)

    assert list_display == TournamentModelAdmin.list_display


async def test_register_admin_model_class_with_sessionmaker():
    class AdminModelClass(ModelAdmin):
        pass

    class OrmModelClass:
        pass

    register_admin_model_class(AdminModelClass, [OrmModelClass], sqlalchemy_sessionmaker="sessionmaker")
    assert AdminModelClass.get_sessionmaker() == "sessionmaker"
    unregister_admin_model_class([OrmModelClass])


async def test_get_admin_or_admin_inline_model():
    class ParentModel:
        pass

    class ChildModel:
        pass

    class InlineAdmin(ModelAdmin):
        model = ChildModel

    class ParentAdmin(ModelAdmin):
        inlines = (InlineAdmin,)

    register_admin_model_class(ParentAdmin, [ParentModel])
    inline = get_admin_or_admin_inline_model("ChildModel")
    assert inline is not None
    assert inline.model_cls is ChildModel
    unregister_admin_model_class([ParentModel])


async def test_generate_models_schema_skips_display_not_in_columns():
    class PlainModel:
        pass

    class PlainAdmin:
        model_name_prefix = None
        list_display = ("name",)
        fields = ()
        list_filter = ()
        sortable_by = ()
        list_display_links = ()
        empty_value_display = "-"
        list_display_widths: ClassVar[dict[str, str]] = {}
        actions_on_top = False
        actions_on_bottom = True
        actions_selection_counter = True
        list_per_page = 10
        search_help_text = ""
        search_fields = ()
        preserve_filters = True
        list_max_show_all = 200
        show_full_result_count = False
        verbose_name = None
        verbose_name_plural = None
        fieldsets = ()
        save_on_top = False
        save_as = False
        save_as_continue = False
        view_on_site = None
        inlines = ()
        actions = ()

        @staticmethod
        def get_model_pk_name(_model):
            return "id"

        def get_model_fields_with_widget_types(self):
            return [
                ModelFieldWidgetSchema(
                    name="name",
                    column_name="name",
                    is_m2m=False,
                    is_pk=False,
                    is_immutable=False,
                    form_widget_type=WidgetType.Input,
                    form_widget_props={"required": True},
                    filter_widget_type=WidgetType.Input,
                    filter_widget_props={},
                )
            ]

        def get_fields_for_serialize(self):
            return {"name", "display_only"}

        async def has_add_permission(self, user_id=None):
            return True

        async def has_change_permission(self, user_id=None):
            return True

        async def has_delete_permission(self, user_id=None):
            return True

        async def has_export_permission(self, user_id=None):
            return True

        @display
        def display_only(self, _obj):
            return "x"

    schema = await generate_models_schema({PlainModel: PlainAdmin()})
    field_names = [f.name for f in schema[0].fields]
    assert "display_only" not in field_names


async def test_generate_models_schema_display_sorter_not_supported():
    class PlainModel:
        pass

    class PlainAdmin:
        model_name_prefix = None
        list_display = ("name", "display_col")
        fields = ()
        list_filter = ()
        sortable_by = ()
        list_display_links = ()
        empty_value_display = "-"
        list_display_widths: ClassVar[dict[str, str]] = {}
        actions_on_top = False
        actions_on_bottom = True
        actions_selection_counter = True
        list_per_page = 10
        search_help_text = ""
        search_fields = ()
        preserve_filters = True
        list_max_show_all = 200
        show_full_result_count = False
        verbose_name = None
        verbose_name_plural = None
        fieldsets = ()
        save_on_top = False
        save_as = False
        save_as_continue = False
        view_on_site = None
        inlines = ()
        actions = ()

        @staticmethod
        def get_model_pk_name(_model):
            return "id"

        def get_model_fields_with_widget_types(self):
            return [
                ModelFieldWidgetSchema(
                    name="name",
                    column_name="name",
                    is_m2m=False,
                    is_pk=False,
                    is_immutable=False,
                    form_widget_type=WidgetType.Input,
                    form_widget_props={"required": True},
                    filter_widget_type=WidgetType.Input,
                    filter_widget_props={},
                )
            ]

        def get_fields_for_serialize(self):
            return {"name", "display_col"}

        async def has_add_permission(self, user_id=None):
            return True

        async def has_change_permission(self, user_id=None):
            return True

        async def has_delete_permission(self, user_id=None):
            return True

        async def has_export_permission(self, user_id=None):
            return True

        @display(sorter="name")
        def display_col(self, _obj):
            return "x"

    with pytest.raises(NotImplementedError):
        await generate_models_schema({PlainModel: PlainAdmin()})


async def test_generate_models_schema_inline_fk_name_error():
    class ParentModel:
        pass

    parent_admin = SimpleNamespace(model_cls=ParentModel)

    class InlineAdmin:
        model_name_prefix = None
        list_display = ()
        fields = ()
        list_filter = ()
        sortable_by = ()
        list_display_links = ()
        empty_value_display = "-"
        list_display_widths: ClassVar[dict[str, str]] = {}
        actions_on_top = False
        actions_on_bottom = True
        actions_selection_counter = True
        list_per_page = 10
        search_help_text = ""
        search_fields = ()
        preserve_filters = True
        list_max_show_all = 200
        show_full_result_count = False
        verbose_name = None
        verbose_name_plural = None
        actions = ()
        fk_name = None
        max_num = 10
        min_num = 1

        @staticmethod
        def get_model_pk_name(_model):
            return "id"

        def get_model_fields_with_widget_types(self):
            # Two FK-like fields to same parent -> auto-detect fails.
            def field(name):
                return ModelFieldWidgetSchema(
                    name=name,
                    column_name=name,
                    is_m2m=False,
                    is_pk=False,
                    is_immutable=False,
                    form_widget_type=WidgetType.AsyncSelect,
                    form_widget_props={"parentModel": "ParentModel"},
                    filter_widget_type=WidgetType.AsyncSelect,
                    filter_widget_props={},
                )

            return [field("parent_one"), field("parent_two")]

        def get_fields_for_serialize(self):
            return {"parent_one", "parent_two"}

        async def has_add_permission(self, user_id=None):
            return True

        async def has_change_permission(self, user_id=None):
            return True

        async def has_delete_permission(self, user_id=None):
            return True

        async def has_export_permission(self, user_id=None):
            return True

    class ChildModel:
        pass

    with pytest.raises(ValueError, match="Couldn't auto-identify fk_name"):
        await generate_models_schema(
            {ChildModel: InlineAdmin()},
            inline_parent_admin_modal=parent_admin,  # type: ignore[arg-type]
        )


async def test_generate_dashboard_widgets_schema():
    from fastadmin.models.base import admin_dashboard_widgets
    from fastadmin.models.schemas import DashboardWidgetType

    class DummyWidget:
        title = "Widget"
        dashboard_widget_type = DashboardWidgetType.ChartLine
        x_field = "x"
        y_field = "y"
        series_field = None
        x_field_filter_widget_type = None
        x_field_filter_widget_props = None
        x_field_periods = None

    prev = admin_dashboard_widgets.copy()
    try:
        admin_dashboard_widgets["DummyWidget"] = DummyWidget()
        widgets = generate_dashboard_widgets_schema()
        assert any(w.key == "DummyWidget" and w.title == "Widget" for w in widgets)
    finally:
        admin_dashboard_widgets.clear()
        admin_dashboard_widgets.update(prev)


def _load_helpers_module_with_blocked_import(blocked_prefix: str) -> ModuleType:
    module_path = Path(__file__).resolve().parents[2] / "fastadmin" / "models" / "helpers.py"
    spec = importlib.util.spec_from_file_location(f"helpers_{blocked_prefix}", module_path)
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)

    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith(blocked_prefix):
            raise ImportError(f"blocked import: {name}")
        return original_import(name, globals, locals, fromlist, level)

    builtins.__import__ = fake_import
    try:
        spec.loader.exec_module(module)
    finally:
        builtins.__import__ = original_import
    return module


def test_helpers_fallback_tortoise_model_class():
    module = _load_helpers_module_with_blocked_import("tortoise")
    assert module.TortoiseModel is not None


def test_helpers_fallback_django_model_class():
    module = _load_helpers_module_with_blocked_import("django")
    assert module.DjangoModel is not None
