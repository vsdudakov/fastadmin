from collections.abc import Sequence
from io import BytesIO, StringIO
from typing import Any

from fastadmin.schemas.api import ExportFormat
from fastadmin.schemas.configuration import WidgetType


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

    # This attribute overrides the default display value for record’s fields that are empty (None, empty string, etc.). The default value is - (a dash).  # noqa: E501
    empty_value_display: str = "-"

    # This attribute, if given, should be a list of field names to exclude from the form.
    exclude: Sequence[str] = ()

    # Use the fields option to make simple layout changes in the forms on the “add” and “change” pages
    # such as showing only a subset of available fields, modifying their order, or grouping them into rows.
    # For more complex layout needs, see the fieldsets option.
    fields: Sequence[str] = ()

    # Set fieldsets to control the layout of admin “add” and “change” pages.
    # fieldsets is a list of two-tuples, in which each two-tuple represents a <fieldset> on the admin form page. (A <fieldset> is a “section” of the form.)  # noqa: E501
    fieldsets: Sequence[tuple[str | None, dict[str, Sequence[str]]]] = ()

    # By default, a ManyToManyField is displayed in the admin site with a <select multiple>.
    # However, multiple-select boxes can be difficult to use when selecting many items.
    # Adding a ManyToManyField to this list will instead use a nifty unobtrusive JavaScript “filter” interface that allows searching within the options.  # noqa: E501
    # The unselected and selected options appear in two boxes side by side. See filter_vertical to use a vertical interface.  # noqa: E501
    filter_horizontal: Sequence[str] = ()

    # Same as filter_horizontal, but uses a vertical display of the filter interface with the box of unselected options appearing above the box of selected options.  # noqa: E501
    filter_vertical: Sequence[str] = ()

    # Not supported setting
    # form

    # Not supported setting
    # inlines

    # Not supported setting
    # formfield_overrides

    # Set list_display to control which fields are displayed on the list page of the admin.
    # If you don’t set list_display, the admin site will display a single column that displays the __str__() representation of each object  # noqa: E501
    list_display: Sequence[str] = ()

    # Use list_display_links to control if and which fields in list_display should be linked to the “change” page for an object.  # noqa: E501
    list_display_links: Sequence[str] = ()

    # Set list_filter to activate filters in the tabel columns of the list page of the admin.
    list_filter: Sequence[str] = ()

    # Set list_max_show_all to control how many items can appear on a “Show all” admin change list page.
    # The admin will display a “Show all” link on the change list only if the total result count is less than or equal to this setting. By default, this is set to 200.  # noqa: E501
    list_max_show_all: int = 200

    # Set list_per_page to control how many items appear on each paginated admin list page. By default, this is set to 10.  # noqa: E501
    list_per_page = 10

    # Set list_select_related to tell ORM to use select_related() in retrieving the list of objects on the admin list page.  # noqa: E501
    # This can save you a bunch of database queries.
    list_select_related: Sequence[str] = ()

    # Set ordering to specify how lists of objects should be ordered in the admin views.
    # This should be a list or tuple in the same format as a model’s ordering parameter.
    ordering: Sequence[str] = ()

    # Not supported setting
    # paginator

    # When set, the given fields will use a bit of JavaScript to populate from the fields assigned.
    # The main use for this functionality is
    # to automatically generate the value for SlugField fields from one or more other fields.
    # The generated value is produced by concatenating the values of the source fields,
    # and then by transforming that result into a valid slug
    # (e.g. substituting dashes for spaces and lowercasing ASCII letters).
    # prepopulated_fields: dict[str, Sequence[str]] = {}

    # By default, applied filters are preserved on the list view after creating, editing, or deleting an object.
    # You can have filters cleared by setting this attribute to False.
    preserve_filters: bool = True

    # By default, FastAPI admin uses a select-box interface (<select>) for fields that are ForeignKey or have choices set.  # noqa: E501
    # If a field is present in radio_fields, FastAPI admin will use a radio-button interface instead.
    radio_fields: Sequence[str] = ()

    # Not supported setting (all fk, m2m uses select js widget as default)
    # autocomplete_fields

    # By default, FastAPI admin uses a select-box interface (<select>) for fields that are ForeignKey.
    # Sometimes you don’t want to incur the overhead of having to select all the related instances to display in the drop-down.  # noqa: E501
    # raw_id_fields is a list of fields you would like to change into an Input widget for either a ForeignKey or ManyToManyField.  # noqa: E501
    raw_id_fields: Sequence[str] = ()

    # By default the admin shows all fields as editable.
    # Any fields in this option (which should be a list or tuple) will display its data as-is and non-editable.
    readonly_fields: Sequence[str] = ()

    # Normally, objects have three save options: “Save”, “Save and continue editing”, and “Save and add another”.
    # If save_as is True, “Save and add another” will be replaced
    # by a “Save as new” button that creates a new object (with a new ID) rather than updating the existing object.
    save_as: bool = False

    # When save_as_continue=True, the default redirect after saving the new object is to the change view for that object.  # noqa: E501
    # If you set save_as_continue=False, the redirect will be to the changelist view.
    save_as_continue: bool = False

    # Normally, the save buttons appear only at the bottom of the forms.
    # If you set save_on_top, the buttons will appear both on the top and the bottom.
    save_on_top: bool = False

    # Set search_fields to enable a search box on the admin list page.
    # This should be set to a list of field names that will be searched whenever somebody submits a search query in that text box.  # noqa: E501
    search_fields: Sequence[str] = ()

    # Set search_help_text to specify a descriptive text for the search box which will be displayed below it.
    search_help_text: str = ""

    # Set show_full_result_count to control whether the full count of objects should be displayed
    # on a filtered admin page (e.g. 99 results (103 total)).
    # If this option is set to False, a text like 99 results (Show all) is displayed instead.
    show_full_result_count: bool = False

    # By default, the list page allows sorting by all model fields
    # If you want to disable sorting for some columns, set sortable_by to a collection (e.g. list, tuple, or set)
    # of the subset of list_display that you want to be sortable.
    # An empty collection disables sorting for all columns.
    sortable_by: Sequence[str] = ()

    # Set view_on_site to control whether or not to display the “View on site” link.
    # This link should bring you to a URL where you can display the saved object.
    view_on_site: str | None = None

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
        format: ExportFormat | None,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> StringIO | BytesIO | None:
        raise NotImplementedError

    def get_form_widget(self, field: str) -> tuple[WidgetType, dict]:
        raise NotImplementedError

    def get_filter_widget(self, field: str) -> tuple[WidgetType, dict]:
        form_widget_type, form_widget_props = self.get_form_widget(field)
        if form_widget_type == WidgetType.Input:
            return WidgetType.Input, {
                **form_widget_props,
                "required": False,
            }
        if form_widget_type == WidgetType.InputNumber:
            return WidgetType.InputNumber, {
                **form_widget_props,
                "required": False,
            }
        if form_widget_type == WidgetType.TextArea:
            return WidgetType.Input, {
                **form_widget_props,
                "required": False,
            }
        if form_widget_type == WidgetType.Select:
            mode_tags = form_widget_props.get("mode") == "tags"
            return WidgetType.Select, {
                **form_widget_props,
                "mode": "tags" if mode_tags else "multiple",
                "required": False,
            }
        if form_widget_type == WidgetType.AsyncSelect:
            return WidgetType.AsyncSelect, {
                **form_widget_props,
                "mode": "multiple",
                "required": False,
            }
        if form_widget_type == WidgetType.AsyncTransfer:
            return WidgetType.AsyncTransfer, {
                **form_widget_props,
                "required": False,
            }
        if form_widget_type == WidgetType.Switch:
            return WidgetType.RadioGroup, {
                **form_widget_props,
                "required": False,
                "options": [
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
            }
        if form_widget_type == WidgetType.Checkbox:
            return WidgetType.RadioGroup, {
                **form_widget_props,
                "required": False,
                "options": [
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
            }
        if form_widget_type == WidgetType.TimePicker:
            return WidgetType.RangePicker, {
                **form_widget_props,
                "required": False,
            }
        if form_widget_type == WidgetType.DatePicker:
            return WidgetType.RangePicker, {
                **form_widget_props,
                "required": False,
            }
        if form_widget_type == WidgetType.DateTimePicker:
            return WidgetType.RangePicker, {
                **form_widget_props,
                "required": False,
            }
        if form_widget_type == WidgetType.RangePicker:
            pass
        if form_widget_type == WidgetType.RadioGroup:
            pass
        if form_widget_type == WidgetType.CheckboxGroup:
            pass
        if form_widget_type == WidgetType.Upload:
            pass
        return WidgetType.Input, {
            **form_widget_props,
            "required": False,
        }

    def get_form_hidden_fields(self) -> Sequence[str]:
        return ()

    def get_list_display(self) -> Sequence[str]:
        return self.list_display

    def get_fields(self) -> Sequence[str]:
        return self.fields

    def get_fieldsets(self) -> Sequence[tuple[str | None, dict[str, Sequence[str]]]]:
        return self.fieldsets

    def has_add_permission(self) -> bool:
        return True

    def has_change_permission(self) -> bool:
        return True

    def has_delete_permission(self) -> bool:
        return True

    def has_export_permission(self) -> bool:
        return True


class ModelAdmin(BaseModelAdmin):
    pass
