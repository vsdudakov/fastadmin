import csv
from collections import OrderedDict
from collections.abc import Sequence
from io import BytesIO, StringIO
from typing import Any
from uuid import UUID

from fastadmin.schemas.api import ExportFormat
from fastadmin.schemas.configuration import WidgetType
from fastadmin.settings import settings


class BaseModelAdmin:
    """Base class for model admin"""

    # Labels for model. We use them in select, autocomplete and other wigets where we represent model items.
    # We user first from label_fields, if it is empty, we use the second and so on.
    # If you don't set this attribute, we will use id attr as label.
    # Example of usage: label_fields = ("name", "email", "id")
    label_fields: Sequence[str] = ()

    # A list of actions to make available on the change list page.
    # You have to implement methods with names like <action_name> in your ModelAdmin class and decorate them with @action decorator.  # noqa: E501
    # Example of usage:
    #
    # actions = ("make_published",)
    # @action(
    #     description="Mark selected stories as published",
    # )
    # async def make_published(self, objs: list[Any]) -> None:
    #     ...
    actions: Sequence[str] = ()

    # Controls where on the page the actions bar appears.
    # By default, the admin changelist displays actions at the top of the page (actions_on_top = False; actions_on_bottom = True).  # noqa: E501
    # Example of usage: actions_on_top = True
    actions_on_top: bool = False

    # Controls where on the page the actions bar appears.
    # By default, the admin changelist displays actions at the top of the page (actions_on_top = False; actions_on_bottom = True).  # noqa: E501
    # Example of usage: actions_on_bottom = False
    actions_on_bottom: bool = True

    # Controls whether a selection counter is displayed next to the action dropdown. By default, the admin changelist will display it  # noqa: E501
    # Example of usage: actions_selection_counter = False
    actions_selection_counter: bool = True

    # Not supported setting
    # date_hierarchy

    # This attribute overrides the default display value for record’s fields that are empty (None, empty string, etc.). The default value is - (a dash).  # noqa: E501
    # Example of usage: empty_value_display = "N/A"
    empty_value_display: str = "-"

    # This attribute, if given, should be a list of field names to exclude from the form.
    # Example of usage: exclude = ("password", "otp")
    exclude: Sequence[str] = ()

    # Use the fields option to make simple layout changes in the forms on the “add” and “change” pages
    # such as showing only a subset of available fields, modifying their order, or grouping them into rows.
    # For more complex layout needs, see the fieldsets option.
    # Example of usage: fields = ("id", "mobile_number", "email", "is_superuser", "is_active", "created_at")
    fields: Sequence[str] = ()

    # Set fieldsets to control the layout of admin “add” and “change” pages.
    # fieldsets is a list of two-tuples, in which each two-tuple represents a <fieldset> on the admin form page. (A <fieldset> is a “section” of the form.)  # noqa: E501
    fieldsets: Sequence[tuple[str | None, dict[str, Sequence[str]]]] = ()

    # By default, a ManyToManyField is displayed in the admin dashboard with a <select multiple>.
    # However, multiple-select boxes can be difficult to use when selecting many items.
    # Adding a ManyToManyField to this list will instead use a nifty unobtrusive JavaScript “filter” interface that allows searching within the options.  # noqa: E501
    # The unselected and selected options appear in two boxes side by side. See filter_vertical to use a vertical interface.  # noqa: E501
    # Example of usage: filter_horizontal = ("groups", "user_permissions")
    filter_horizontal: Sequence[str] = ()

    # Same as filter_horizontal, but uses a vertical display of the filter interface with the box of unselected options appearing above the box of selected options.  # noqa: E501
    # Example of usage: filter_vertical = ("groups", "user_permissions")
    filter_vertical: Sequence[str] = ()

    # Not supported setting
    # form

    # Not supported setting
    # inlines

    # Not supported setting
    # formfield_overrides

    # Set list_display to control which fields are displayed on the list page of the admin.
    # If you don’t set list_display, the admin site will display a single column that displays the __str__() representation of each object  # noqa: E501
    # Example of usage: list_display = ("id", "mobile_number", "email", "is_superuser", "is_active", "created_at")
    list_display: Sequence[str] = ()

    # Use list_display_links to control if and which fields in list_display should be linked to the “change” page for an object.  # noqa: E501
    # Example of usage: list_display_links = ("id", "mobile_number", "email")
    list_display_links: Sequence[str] = ()

    # Set list_filter to activate filters in the tabel columns of the list page of the admin.
    # Example of usage: list_filter = ("is_superuser", "is_active", "created_at")
    list_filter: Sequence[str] = ()

    # Set list_max_show_all to control how many items can appear on a “Show all” admin change list page.
    # The admin will display a “Show all” link on the change list only if the total result count is less than or equal to this setting. By default, this is set to 200.  # noqa: E501
    # Example of usage: list_max_show_all = 100
    list_max_show_all: int = 200

    # Set list_per_page to control how many items appear on each paginated admin list page. By default, this is set to 10.  # noqa: E501
    # Example of usage: list_per_page = 50
    list_per_page = 10

    # Set list_select_related to tell ORM to use select_related() in retrieving the list of objects on the admin list page.  # noqa: E501
    # This can save you a bunch of database queries.
    # Example of usage: list_select_related = ("user",)
    list_select_related: Sequence[str] = ()

    # Set ordering to specify how lists of objects should be ordered in the admin views.
    # This should be a list or tuple in the same format as a model’s ordering parameter.
    # Example of usage: ordering = ("-created_at",)
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
    # Example of usage: preserve_filters = False
    preserve_filters: bool = True

    # By default, FastAPI admin uses a select-box interface (<select>) for fields that are ForeignKey or have choices set.  # noqa: E501
    # If a field is present in radio_fields, FastAPI admin will use a radio-button interface instead.
    # Example of usage: radio_fields = ("user",)
    radio_fields: Sequence[str] = ()

    # Not supported setting (all fk, m2m uses select js widget as default)
    # autocomplete_fields

    # By default, FastAPI admin uses a select-box interface (<select>) for fields that are ForeignKey.
    # Sometimes you don’t want to incur the overhead of having to select all the related instances to display in the drop-down.  # noqa: E501
    # raw_id_fields is a list of fields you would like to change into an Input widget for either a ForeignKey or ManyToManyField.  # noqa: E501
    # Example of usage: raw_id_fields = ("user",)
    raw_id_fields: Sequence[str] = ()

    # By default the admin shows all fields as editable.
    # Any fields in this option (which should be a list or tuple) will display its data as-is and non-editable.
    # Example of usage: readonly_fields = ("created_at",)
    readonly_fields: Sequence[str] = ()

    # Normally, objects have three save options: “Save”, “Save and continue editing”, and “Save and add another”.
    # If save_as is True, “Save and add another” will be replaced
    # by a “Save as new” button that creates a new object (with a new ID) rather than updating the existing object.
    # Example of usage: save_as = True
    save_as: bool = False

    # When save_as_continue=True, the default redirect after saving the new object is to the change view for that object.  # noqa: E501
    # If you set save_as_continue=False, the redirect will be to the changelist view.
    # Example of usage: save_as_continue = False
    save_as_continue: bool = False

    # Normally, the save buttons appear only at the bottom of the forms.
    # If you set save_on_top, the buttons will appear both on the top and the bottom.
    # Example of usage: save_on_top = True
    save_on_top: bool = False

    # Set search_fields to enable a search box on the admin list page.
    # This should be set to a list of field names that will be searched whenever somebody submits a search query in that text box.  # noqa: E501
    # Example of usage: search_fields = ("mobile_number", "email")
    search_fields: Sequence[str] = ()

    # Set search_help_text to specify a descriptive text for the search box which will be displayed below it.
    # Example of usage: search_help_text = "Search by mobile number or email"
    search_help_text: str = ""

    # Set show_full_result_count to control whether the full count of objects should be displayed
    # on a filtered admin page (e.g. 99 results (103 total)).
    # If this option is set to False, a text like 99 results (Show all) is displayed instead.
    # Example of usage: show_full_result_count = True
    show_full_result_count: bool = False

    # By default, the list page allows sorting by all model fields
    # If you want to disable sorting for some columns, set sortable_by to a collection (e.g. list, tuple, or set)
    # of the subset of list_display that you want to be sortable.
    # An empty collection disables sorting for all columns.
    # Example of usage: sortable_by = ("mobile_number", "email")
    sortable_by: Sequence[str] = ()

    # Set view_on_site to control whether or not to display the “View on site” link.
    # This link should bring you to a URL where you can display the saved object.
    # Example of usage: view_on_site = "http://example.com"
    view_on_site: str | None = None

    def __init__(self, model_cls: Any):
        """This method is used to initialize admin class.

        :params model_cls: an orm/db model class.
        """
        self.model_cls = model_cls

    async def authenticate(self, username: str, password: str) -> UUID | int | None:
        """This method is used to implement authentication for settings.ADMIN_USER_MODEL orm/db model.

        :params username: a value for user model settings.ADMIN_USER_MODEL_USERNAME_FIELD field.
        :params password: a password.
        :return: An user id or None.
        """
        raise NotImplementedError

    async def save_model(self, id: UUID | int | None, payload: dict) -> dict | None:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a payload from request.
        :return: A saved object or None.
        """
        raise NotImplementedError

    async def delete_model(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        raise NotImplementedError

    async def get_obj(self, id: UUID | int) -> dict | None:
        """This method is used to get orm/db model object by id.

        :params id: an id of object.
        :return: An object or None.
        """
        raise NotImplementedError

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[dict], int]:
        """This method is used to get list of orm/db model objects.

        :params offset: an offset for pagination.
        :params limit: a limit for pagination.
        :params search: a search query.
        :params sort_by: a sort by field name.
        :params filters: a dict of filters.
        :return: A tuple of list of objects and total count.
        """
        raise NotImplementedError

    def get_model_fields(self) -> OrderedDict[str, dict]:
        """This method is used to get all orm/db model fields
        with saving ordering (non relations, fk, o2o, m2m).

        :return: An OrderedDict of model fields.
        """
        raise NotImplementedError

    def get_form_widget(self, field_name: str) -> tuple[WidgetType, dict]:
        """This method is used to get form item widget
        for field from orm/db model.

        :params field_name: a model field name.
        :return: A tuple of widget type and widget props.
        """
        raise NotImplementedError

    async def get_export(
        self,
        export_format: ExportFormat | None,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> StringIO | BytesIO | None:
        """This method is used to get export data (str or bytes stream).

        :params export_format: a n export format (CSV at default).
        :params offset: an offset for pagination.
        :params limit: a limit for pagination.
        :params search: a search query.
        :params sort_by: a sort by field name.
        :params filters: a dict of filters.
        :return: A StringIO or BytesIO object.
        """
        objs, _ = await self.get_list(offset=offset, limit=limit, search=search, sort_by=sort_by, filters=filters)
        model_fields = self.get_model_fields()
        export_fields = [f for f, v in model_fields.items() if not v.get("is_m2m") and not v.get("form_hidden")]
        if not export_format or export_format == ExportFormat.CSV:
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=export_fields)
            writer.writeheader()
            for obj in objs:
                obj_dict = {fieldname: getattr(obj, fieldname, None) for fieldname in export_fields}
                writer.writerow(obj_dict)
            output.seek(0)
            return output
        return None

    def get_filter_widget(self, field_name: str) -> tuple[WidgetType, dict]:
        """This method is used to get filter widget for tabel columns
        for field from orm/db model from list_filter parameter.

        :params field_name: a model field name.
        :return: A tuple of widget type and widget props.
        """
        form_widget_type, form_widget_props = self.get_form_widget(field_name)
        match form_widget_type:
            case WidgetType.Input:
                return WidgetType.Input, {
                    **form_widget_props,
                    "required": False,
                }
            case WidgetType.InputNumber:
                return WidgetType.InputNumber, {
                    **form_widget_props,
                    "required": False,
                }
            case WidgetType.TextArea:
                return WidgetType.Input, {
                    **form_widget_props,
                    "required": False,
                }
            case WidgetType.Select:
                mode_tags = form_widget_props.get("mode") == "tags"
                return WidgetType.Select, {
                    **form_widget_props,
                    "mode": "tags" if mode_tags else "multiple",
                    "required": False,
                }
            case WidgetType.AsyncSelect:
                return WidgetType.AsyncSelect, {
                    **form_widget_props,
                    "mode": "multiple",
                    "required": False,
                }
            case WidgetType.AsyncTransfer:
                return WidgetType.AsyncTransfer, {
                    **form_widget_props,
                    "required": False,
                }
            case WidgetType.Switch:
                return WidgetType.RadioGroup, {
                    **form_widget_props,
                    "required": False,
                    "options": [
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ],
                }
            case WidgetType.Checkbox:
                return WidgetType.RadioGroup, {
                    **form_widget_props,
                    "required": False,
                    "options": [
                        {"label": "Yes", "value": True},
                        {"label": "No", "value": False},
                    ],
                }
            case WidgetType.TimePicker:
                return WidgetType.RangePicker, {
                    **form_widget_props,
                    "required": False,
                    "format": settings.ADMIN_TIME_FORMAT,
                    "showTime": True,
                }
            case WidgetType.DatePicker:
                return WidgetType.RangePicker, {
                    **form_widget_props,
                    "required": False,
                    "format": settings.ADMIN_DATE_FORMAT,
                }
            case WidgetType.DateTimePicker:
                return WidgetType.RangePicker, {
                    **form_widget_props,
                    "required": False,
                    "format": settings.ADMIN_DATETIME_FORMAT,
                    "showTime": True,
                }
            case WidgetType.RadioGroup:
                return WidgetType.CheckboxGroup, {
                    **form_widget_props,
                    "required": False,
                }
            case WidgetType.CheckboxGroup:
                return WidgetType.CheckboxGroup, {
                    **form_widget_props,
                    "required": False,
                }
            # case WidgetType.RangePicker:
            # case WidgetType.Upload:
            case _:
                return WidgetType.Input, {
                    **form_widget_props,
                    "required": False,
                }

    def get_list_display(self) -> Sequence[str]:
        """This method is used to get list of fields for display on table view.

        :return: A list of model field names.
        """
        list_display = self.list_display
        model_fields = self.get_model_fields()
        if not list_display:
            return [f for f in self.get_fields() if model_fields[f].get("is_pk")]
        return [f for f in list_display if f in model_fields]

    def get_fields(self) -> Sequence[str]:
        """This method is used to get list of fields for display on form view.

        :return: A list of model field names.
        """
        fields = self.fields
        model_fields = self.get_model_fields()
        if not fields:
            return [f for f in model_fields if not self.exclude or f not in self.exclude]
        return [f for f in fields if f in model_fields]

    # def get_fieldsets(self) -> Sequence[tuple[str | None, dict[str, Sequence[str]]]]:
    #     """This method is used to get fieldsets data for form view.

    #     :return: A list of fieldsets data.
    #     """
    #     return self.fieldsets

    def has_add_permission(self) -> bool:
        """This method is used to check if user has permission to add new model instance.

        :return: A boolean value.
        """
        return True

    def has_change_permission(self) -> bool:
        """This method is used to check if user has permission to change model instance.

        :return: A boolean value.
        """
        return True

    def has_delete_permission(self) -> bool:
        """This method is used to check if user has permission to delete model instance.

        :return: A boolean value.
        """
        return True

    def has_export_permission(self) -> bool:
        """This method is used to check if user has permission to export model instance.

        :return: A boolean value.
        """
        return True


class ModelAdmin(BaseModelAdmin):
    """This class is used to create admin model class."""

    pass
