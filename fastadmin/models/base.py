import csv
import inspect
import json
from collections.abc import Sequence
from io import BytesIO, StringIO
from typing import Any
from uuid import UUID

from asgiref.sync import sync_to_async

from fastadmin.api.helpers import is_valid_base64
from fastadmin.api.schemas import ExportFormat
from fastadmin.models.schemas import DashboardWidgetType, ModelFieldWidgetSchema, WidgetType


class BaseModelAdmin:
    """Base class for model admin"""

    # Use it only if you use several orms in your project.
    model_name_prefix: str | None = None

    # A list of actions to make available on the change list page.
    # You have to implement methods with names like action_name in your ModelAdmin class and decorate them with @action decorator.
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
    # By default, the admin changelist displays actions at the top of the page (actions_on_top = False; actions_on_bottom = True).
    # Example of usage: actions_on_top = True
    actions_on_top: bool = False

    # Controls where on the page the actions bar appears.
    # By default, the admin changelist displays actions at the top of the page (actions_on_top = False; actions_on_bottom = True).
    # Example of usage: actions_on_bottom = False
    actions_on_bottom: bool = True

    # Controls whether a selection counter is displayed next to the action dropdown. By default, the admin changelist will display it
    # Example of usage: actions_selection_counter = False
    actions_selection_counter: bool = True

    # Not supported setting
    # date_hierarchy

    # This attribute overrides the default display value for record's fields that are empty (None, empty string, etc.). The default value is - (a dash).
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
    # fieldsets is a list of two-tuples, in which each two-tuple represents a fieldset on the admin form page. (A fieldset is a “section” of the form.)
    fieldsets: Sequence[tuple[str | None, dict[str, Sequence[str]]]] = ()

    # By default, a ManyToManyField is displayed in the admin dashboard with a select multiple.
    # However, multiple-select boxes can be difficult to use when selecting many items.
    # Adding a ManyToManyField to this list will instead use a nifty unobtrusive JavaScript “filter” interface that allows searching within the options.
    # The unselected and selected options appear in two boxes side by side. See filter_vertical to use a vertical interface.
    # Example of usage: filter_horizontal = ("groups", "user_permissions")
    filter_horizontal: Sequence[str] = ()

    # Same as filter_horizontal, but uses a vertical display of the filter interface with the box of unselected options appearing above the box of selected options.
    # Example of usage: filter_vertical = ("groups", "user_permissions")
    filter_vertical: Sequence[str] = ()

    # Not supported setting
    # form

    # This provides a quick-and-dirty way to override some of the Field options for use in the admin.
    # formfield_overrides is a dictionary mapping a field class to a dict
    # of arguments to pass to the field at construction time.
    # Example of usage:
    # formfield_overrides = {
    #     "description": (WidgetType.RichTextArea, {})
    # }
    formfield_overrides: dict[str, tuple[WidgetType, dict]] = {}

    # Set list_display to control which fields are displayed on the list page of the admin.
    # If you don't set list_display, the admin site will display a single column that displays the __str__() representation of each object
    # Example of usage: list_display = ("id", "mobile_number", "email", "is_superuser", "is_active", "created_at")
    list_display: Sequence[str] = ()

    # Use list_display_links to control if and which fields in list_display should be linked to the “change” page for an object.
    # Example of usage: list_display_links = ("id", "mobile_number", "email")
    list_display_links: Sequence[str] = ()

    # A dictionary containing the field names and the corresponding widget type and
    # column widths (px, %) for the list view.
    # Example of usage:
    # list_display_widths = {
    #     "id": "100px",
    # }
    list_display_widths: dict[str, str] = {}

    # Set list_filter to activate filters in the tabel columns of the list page of the admin.
    # Example of usage: list_filter = ("is_superuser", "is_active", "created_at")
    list_filter: Sequence[str] = ()

    # By default, applied filters are preserved on the list view after creating, editing, or deleting an object.
    # You can have filters cleared by setting this attribute to False.
    # Example of usage: preserve_filters = False
    preserve_filters: bool = True

    # Set list_max_show_all to control how many items can appear on a “Show all” admin change list page.
    # The admin will display a “Show all” link on the change list only if the total result count is less than or equal to this setting. By default, this is set to 200.
    # Example of usage: list_max_show_all = 100
    list_max_show_all: int = 200

    # Set list_per_page to control how many items appear on each paginated admin list page. By default, this is set to 10.
    # Example of usage: list_per_page = 50
    list_per_page = 10

    # Set list_select_related to tell ORM to use select_related() in retrieving the list of objects on the admin list page.
    # This can save you a bunch of database queries.
    # Example of usage: list_select_related = ("user",)
    list_select_related: Sequence[str] = ()

    # Set ordering to specify how lists of objects should be ordered in the admin views.
    # This should be a list or tuple in the same format as a model's ordering parameter.
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

    # By default, FastAPI admin uses a select-box interface (select) for fields that are ForeignKey or have choices set.
    # If a field is present in radio_fields, FastAPI admin will use a radio-button interface instead.
    # Example of usage: radio_fields = ("user",)
    radio_fields: Sequence[str] = ()

    # Not supported setting (all fk, m2m uses select js widget as default)
    # autocomplete_fields

    # By default, FastAPI admin uses a select-box interface (select) for fields that are ForeignKey.
    # Sometimes you don't want to incur the overhead of having to select all the related instances to display in the drop-down.
    # raw_id_fields is a list of fields you would like to change into an Input widget for either a ForeignKey or ManyToManyField.
    # Example of usage: raw_id_fields = ("user",)
    raw_id_fields: Sequence[str] = ()

    # By default the admin shows all fields as editable.
    # Any fields in this option (which should be a list or tuple) will display its data as-is and non-editable.
    # Example of usage: readonly_fields = ("created_at",)
    readonly_fields: Sequence[str] = ()

    # Set search_fields to enable a search box on the admin list page.
    # This should be set to a list of field names that will be searched whenever somebody submits a search query in that text box.
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

    # An override to the verbose_name from the model's inner Meta class.
    verbose_name: str | None = None

    # An override to the verbose_name_plural from the model's inner Meta class.
    verbose_name_plural: str | None = None

    def __init__(self, model_cls: Any):
        """This method is used to initialize admin class.

        :params model_cls: an orm/db model class.
        """
        self.model_cls = model_cls

    @staticmethod
    def get_model_pk_name(orm_model_cls: Any) -> str:
        """This method is used to get model pk name.

        :return: A str.
        """
        raise NotImplementedError

    def get_model_fields_with_widget_types(
        self,
        with_m2m: bool | None = None,
        with_upload: bool | None = None,
    ) -> list[ModelFieldWidgetSchema]:
        """This method is used to get model fields with widget types.

        :params with_m2m: a flag to include m2m fields.
        :params with_upload: a flag to include upload fields.
        :return: A list of ModelFieldWidgetSchema.
        """
        raise NotImplementedError

    async def orm_get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[Any], int]:
        """This method is used to get list of orm/db model objects.

        :params offset: an offset for pagination.
        :params limit: a limit for pagination.
        :params search: a search query.
        :params sort_by: a sort by field name.
        :params filters: a dict of filters.
        :return: A tuple of list of objects and total count.
        """
        raise NotImplementedError

    async def orm_get_obj(self, id: UUID | int) -> Any | None:
        """This method is used to get orm/db model object.

        :params id: an id of object.
        :return: An object or None.
        """
        raise NotImplementedError

    async def orm_save_obj(self, id: UUID | Any | None, payload: dict) -> Any:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a dict of payload.
        :return: An object.
        """
        raise NotImplementedError

    async def orm_delete_obj(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        raise NotImplementedError

    async def orm_get_m2m_ids(self, obj: Any, field: str) -> list[int | UUID]:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.

        :return: A list of ids.
        """
        raise NotImplementedError

    async def orm_save_m2m_ids(self, obj: Any, field: str, ids: list[int | UUID]) -> None:
        """This method is used to get m2m ids.

        :params obj: an object.
        :params field: a m2m field name.
        :params ids: a list of ids.

        :return: A list of ids.
        """
        raise NotImplementedError

    async def orm_save_upload_field(self, obj: Any, field: str, base64: str) -> None:
        """This method is used to save upload field.

        :params obj: an object.
        :params field: a m2m field name.
        :params base64: a base64 string.

        :return: A list of ids.
        """
        raise NotImplementedError

    @classmethod
    def get_sessionmaker(cls) -> Any:
        """This method is used to get db session maker for sqlalchemy.

        :return: A db session maker.
        """
        return cls.db_session_maker

    @classmethod
    def set_sessionmaker(cls, db_session_maker: Any) -> None:
        """This method is used to set db session maker for sqlalchemy.

        :params db_session: a db session maker.
        :return: None.
        """
        cls.db_session_maker = db_session_maker

    def get_fields_for_serialize(self) -> set[str]:
        """This method is used to get fields for serialize.

        :return: A set of fields.
        """
        fields = self.get_model_fields_with_widget_types()
        fields_for_serialize = {field.name for field in fields}
        if self.fields:
            fields_for_serialize &= set(self.fields)
        if self.exclude:
            fields_for_serialize -= set(self.exclude)
        if self.list_display:
            fields_for_serialize |= set(self.list_display)
        return fields_for_serialize

    async def serialize_obj_attributes(
        self, obj: Any, attributes_to_serizalize: list[ModelFieldWidgetSchema]
    ) -> dict[str, Any]:
        """Serialize orm model obj attribute to dict.

        :params obj: an object.
        :params attributes_to_serizalize: a list of attributes to serialize.
        :return: A dict of serialized attributes.
        """
        serialized_dict = {field.name: getattr(obj, field.column_name) for field in attributes_to_serizalize}
        if inspect.iscoroutinefunction(obj.__str__):
            str_fn = obj.__str__
        else:
            str_fn = sync_to_async(obj.__str__)
        serialized_dict["__str__"] = await str_fn()
        return serialized_dict

    async def serialize_obj(self, obj: Any, list_view: bool = False) -> dict:
        """Serialize orm model obj to dict.

        :params obj: an object.
        :params exclude_fields: a list of fields to exclude.
        :return: A dict.
        """
        fields = self.get_model_fields_with_widget_types()
        fields_for_serialize = self.get_fields_for_serialize()

        obj_dict = {}
        attributes_to_serizalize = []
        for field in fields:
            if field.name not in fields_for_serialize:
                continue
            if field.is_m2m and list_view:
                continue
            if field.is_m2m:
                obj_dict[field.name] = await self.orm_get_m2m_ids(obj, field.column_name)
            else:
                attributes_to_serizalize.append(field)

        obj_dict.update(await self.serialize_obj_attributes(obj, attributes_to_serizalize))

        for field_name in fields_for_serialize:
            display_field_function = getattr(self, field_name, None)
            if not display_field_function or not hasattr(display_field_function, "is_display"):
                continue

            if inspect.iscoroutinefunction(display_field_function):
                display_field_function_fn = display_field_function
            else:
                display_field_function_fn = sync_to_async(display_field_function)

            obj_dict[field_name] = await display_field_function_fn(obj)

        return obj_dict

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[dict], int]:
        """This method is used to get list of seriaized objects.

        :params offset: an offset for pagination.
        :params limit: a limit for pagination.
        :params search: a search query.
        :params sort_by: a sort by field name.
        :params filters: a dict of filters.
        :return: A tuple of list of dict and total count.
        """
        objs, total = await self.orm_get_list(
            offset=offset,
            limit=limit,
            search=search,
            sort_by=sort_by,
            filters=filters,
        )
        serialized_objs = []
        for obj in objs:
            serialized_objs.append(await self.serialize_obj(obj, list_view=True))
        return serialized_objs, total

    async def get_obj(self, id: UUID | int) -> dict | None:
        """This method is used to get serialized object by id.

        :params id: an id of object.
        :return: A dict or None.
        """
        obj = await self.orm_get_obj(id)
        if not obj:
            return None
        return await self.serialize_obj(obj)

    async def save_model(self, id: UUID | int | None, payload: dict) -> dict | None:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a payload from request.
        :return: A saved object or None.
        """
        fields = self.get_model_fields_with_widget_types(with_m2m=False, with_upload=False)
        m2m_fields = self.get_model_fields_with_widget_types(with_m2m=True)
        upload_fields = self.get_model_fields_with_widget_types(with_upload=True)

        fields_payload = {field.column_name: payload[field.name] for field in fields if field.name in payload}
        obj = await self.orm_save_obj(id, fields_payload)
        if not obj:
            return None

        for upload_field in upload_fields:
            if upload_field.name in payload and is_valid_base64(payload[upload_field.name]):
                await self.orm_save_upload_field(obj, upload_field.column_name, payload[upload_field.name])

        for m2m_field in m2m_fields:
            if m2m_field.name in payload:
                await self.orm_save_m2m_ids(obj, m2m_field.column_name, payload[m2m_field.name])

        return await self.serialize_obj(obj)

    async def delete_model(self, id: UUID | int) -> None:
        """This method is used to delete orm/db model object.

        :params id: an id of object.
        :return: None.
        """
        await self.orm_delete_obj(id)

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
        objs, _ = await self.orm_get_list(offset=offset, limit=limit, search=search, sort_by=sort_by, filters=filters)
        fields = self.get_model_fields_with_widget_types(with_m2m=False)

        export_fields = [f.name for f in fields]

        match export_format:
            case ExportFormat.CSV:
                output = StringIO()
                writer = csv.DictWriter(output, fieldnames=export_fields)
                writer.writeheader()
                for obj in objs:
                    obj_dict = await self.serialize_obj(obj, list_view=True)
                    obj_dict = {k: v for k, v in obj_dict.items() if k in export_fields}
                    writer.writerow(obj_dict)
                output.seek(0)
                return output
            case ExportFormat.JSON:

                class JSONEncoder(json.JSONEncoder):
                    def default(self, obj):
                        try:
                            return super().default(obj)
                        except TypeError:
                            return str(obj)

                output = StringIO()
                json.dump([await self.serialize_obj(obj, list_view=True) for obj in objs], output, cls=JSONEncoder)
                output.seek(0)
                return output
            case _:
                return None

    def has_add_permission(self, user_id: UUID | int | None = None) -> bool:
        """This method is used to check if user has permission to add new model instance.

        :param user_id: The user id.
        :return: A boolean value.
        """
        return True

    def has_change_permission(self, user_id: UUID | int | None = None) -> bool:
        """This method is used to check if user has permission to change model instance.

        :param user_id: The user id.
        :return: A boolean value.
        """
        return True

    def has_delete_permission(self, user_id: UUID | int | None = None) -> bool:
        """This method is used to check if user has permission to delete model instance.

        :param user_id: The user id.
        :return: A boolean value.
        """
        return True

    def has_export_permission(self, user_id: UUID | int | None = None) -> bool:
        """This method is used to check if user has permission to export model instance.

        :param user_id: The user id.
        :return: A boolean value.
        """
        return True


class InlineModelAdmin(BaseModelAdmin):
    """This class is used to create admin inline model class."""

    # The model class which the inline is using. This is required.
    model: Any

    # The name of the foreign key on the model.
    # In most cases this will be dealt with automatically, but fk_name must be specified explicitly
    # if there are more than one foreign key to the same parent model.
    fk_name: str | None = None

    # This controls the maximum number of forms to show in the inline.
    # This doesn't directly correlate to the number of objects, but can if the value is small enough.
    # See Limiting the number of editable objects for more information.
    max_num: int = 10

    # This controls the minimum number of forms to show in the inline.
    min_num: int = 1


class ModelAdmin(BaseModelAdmin):
    """This class is used to create admin model class."""

    # Normally, objects have three save options: “Save”, “Save and continue editing”, and “Save and add another”.
    # If save_as is True, “Save and add another” will be replaced
    # by a “Save as new” button that creates a new object (with a new ID) rather than updating the existing object.
    # Example of usage: save_as = True
    save_as: bool = False

    # When save_as_continue=True, the default redirect after saving the new object is to the change view for that object.
    # If you set save_as_continue=False, the redirect will be to the changelist view.
    # Example of usage: save_as_continue = False
    save_as_continue: bool = False

    # Normally, the save buttons appear only at the bottom of the forms.
    # If you set save_on_top, the buttons will appear both on the top and the bottom.
    # Example of usage: save_on_top = True
    save_on_top: bool = False

    # Set view_on_site to control whether or not to display the “View on site” link.
    # This link should bring you to a URL where you can display the saved object.
    # Example of usage: view_on_site = "http://example.com"
    view_on_site: str | None = None

    # Inlines
    inlines: Sequence[type[InlineModelAdmin]] = ()

    async def authenticate(self, username: str, password: str) -> UUID | int | None:
        """This method is used to implement authentication for settings.ADMIN_USER_MODEL orm/db model.

        :params username: a value for user model settings.ADMIN_USER_MODEL_USERNAME_FIELD field.
        :params password: a password.
        :return: An user id or None.
        """
        raise NotImplementedError

    async def change_password(self, id: UUID | int, password: str) -> None:
        """This method is used to change user password.

        :params id: An user id.
        :params password: A new password.
        """
        raise NotImplementedError


class DashboardWidgetAdmin:
    title: str
    dashboard_widget_type: DashboardWidgetType
    x_field: str
    y_field: str | None = None
    series_field: str | None = None
    x_field_filter_widget_type: WidgetType | None = None
    x_field_filter_widget_props: dict[str, Any] | None = None
    x_field_periods: list[str] | None = None

    async def get_data(
        self,
        min_x_field: str | None = None,
        max_x_field: str | None = None,
        period_x_field: str | None = None,
    ) -> dict[str, Any]:
        """This method is used to get data for dashboard widget.

        :params min_x_field: A minimum value for x_field.
        :params max_x_field: A maximum value for x_field.
        :params period_x_field: A period value for x_field.
        :return: A dict with data.
        """
        raise NotImplementedError


admin_models: dict[Any, ModelAdmin] = {}
admin_dashboard_widgets: dict[str, DashboardWidgetAdmin] = {}
