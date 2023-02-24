from io import BytesIO, StringIO
from typing import Any, Sequence

from fastapi_admin.schemas.api import ExportFormat
from fastapi_admin.schemas.configuration import WidgetType


class BaseModelAdmin:
    # Not supported setting
    # actions

    # Not supported setting
    # actions_on_top

    # Not supported setting
    # actions_on_bottom

    # Not supported setting
    # actions_selection_counter

    # Not supported setting
    # date_hierarchy

    # This attribute overrides the default display value for record’s fields that are empty (None, empty string, etc.). The default value is - (a dash).
    empty_value_display: str = "-"

    # This attribute, if given, should be a list of field names to exclude from the form.
    exclude: Sequence[str] = ()

    # Use the fields option to make simple layout changes in the forms on the “add” and “change” pages
    # such as showing only a subset of available fields, modifying their order, or grouping them into rows.
    # For more complex layout needs, see the fieldsets option.
    fields: Sequence[str] = ()

    # Set fieldsets to control the layout of admin “add” and “change” pages.
    # fieldsets is a list of two-tuples, in which each two-tuple represents a <fieldset> on the admin form page. (A <fieldset> is a “section” of the form.)
    fieldsets: Sequence[tuple[str | None, dict[str, Sequence[str]]]] = ()

    # Not supported setting
    # filter_horizontal

    # Not supported setting
    # filter_vertical

    # Not supported setting
    # form

    # Not supported setting
    # inlines

    # Not supported setting
    # formfield_overrides

    # Set list_display to control which fields are displayed on the list page of the admin.
    # If you don’t set list_display, the admin site will display a single column that displays the __str__() representation of each object
    list_display: Sequence[str] = ()

    # Use list_display_links to control if and which fields in list_display should be linked to the “change” page for an object.
    list_display_links: Sequence[str] = ()

    # Set list_filter to activate filters in the tabel columns of the list page of the admin.
    list_filter: Sequence[str] = ()

    # Not supported setting
    # list_max_show_all

    # Set list_per_page to control how many items appear on each paginated admin list page. By default, this is set to 10.
    list_per_page = 10

    # Set list_select_related to tell ORM to use select_related() in retrieving the list of objects on the admin list page.
    # This can save you a bunch of database queries.
    list_select_related: Sequence[str] = ()

    # Set ordering to specify how lists of objects should be ordered in the admin views.
    # This should be a list or tuple in the same format as a model’s ordering parameter.
    ordering: Sequence[str] = ()

    # Not supported setting
    # paginator

    # Not supported setting
    # prepopulated_fields

    # Not supported setting
    # preserve_filters

    # By default, FastAPI admin uses a select-box interface (<select>) for fields that are ForeignKey or have choices set.
    # If a field is present in radio_fields, FastAPI admin will use a radio-button interface instead.
    radio_fields: Sequence[str] = ()

    # Not supported setting
    # autocomplete_fields

    # By default, FastAPI admin uses a select-box interface (<select>) for fields that are ForeignKey.
    # Sometimes you don’t want to incur the overhead of having to select all the related instances to display in the drop-down.
    # raw_id_fields is a list of fields you would like to change into an Input widget for either a ForeignKey or ManyToManyField.
    raw_id_fields: Sequence[str] = ()

    # By default the admin shows all fields as editable.
    # Any fields in this option (which should be a list or tuple) will display its data as-is and non-editable.
    readonly_fields: Sequence[str] = ()

    hidden_fields: Sequence[str] = ()

    # Not supported setting
    # save_as

    # Not supported setting
    # save_as_continue

    # Normally, the save buttons appear only at the bottom of the forms.
    # If you set save_on_top, the buttons will appear both on the top and the bottom.
    save_on_top: bool = False

    # Set search_fields to enable a search box on the admin list page.
    # This should be set to a list of field names that will be searched whenever somebody submits a search query in that text box.
    search_fields: Sequence[str] = ()

    # Set search_help_text to specify a descriptive text for the search box which will be displayed below it.
    search_help_text: str = ""

    # Not supported setting
    # show_full_result_count

    # By default, the list page allows sorting by all model fields
    # If you want to disable sorting for some columns, set sortable_by to a collection (e.g. list, tuple, or set) of the subset of list_display that you want to be sortable.
    # An empty collection disables sorting for all columns.
    sortable_by: Sequence[str] = ()

    # Not supported setting
    # view_on_site

    def __init__(self, model_cls: Any):
        self.model_cls = model_cls

    async def save_model(self, obj: Any, payload: dict, add: bool = False) -> None:
        raise NotImplementedError

    async def delete_model(self, obj: Any) -> None:
        raise NotImplementedError

    async def get_obj(self, id: str) -> Any | None:
        raise NotImplementedError

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[Any], int]:
        raise NotImplementedError

    async def get_export(
        self,
        format: ExportFormat,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> StringIO | BytesIO | None:
        raise NotImplementedError

    async def get_form_widget(self, field: str) -> tuple[WidgetType, dict]:
        raise NotImplementedError

    async def get_filter_widget(self, field: str) -> tuple[WidgetType, dict]:
        raise NotImplementedError

    async def get_hidden_fields(self) -> Sequence[str]:
        return self.hidden_fields

    async def get_list_display(self) -> Sequence[str]:
        return self.list_display

    async def get_fields(self) -> Sequence[str]:
        return self.fields

    async def get_fieldsets(self) -> Sequence[str]:
        return self.fieldsets

    async def has_add_permission(self) -> bool:
        return True

    async def has_change_permission(self) -> bool:
        return True

    async def has_delete_permission(self) -> bool:
        return True

    async def has_export_permission(self) -> bool:
        return True


class ModelAdmin(BaseModelAdmin):
    pass
