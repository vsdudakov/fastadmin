from typing import Any, Sequence

from fastapi_admin.api.schemas.configuration import WidgetType


class ModelAdmin:
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

    async def get_form_widget(self, field: str) -> tuple[WidgetType, WidgetType]:
        raise NotImplementedError

    async def get_filter_widget(self, field: str) -> tuple[WidgetType, WidgetType]:
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


class TortoiseModelAdmin(ModelAdmin):
    def _get_model_fields(self) -> dict[str, Any]:
        return self.model_cls._meta.fields_map

    async def save_model(self, obj: Any, payload: dict, add: bool = False) -> None:
        for key, value in payload.items():
            setattr(obj, key, value)
        await obj.save(update_fields=payload.keys() if not add else None)

    async def delete_model(self, obj: Any) -> None:
        await obj.delete()

    async def get_obj(self, id: str) -> Any | None:
        return await self.model_cls.filter(id=id).first()

    async def get_list(
        self,
        offset: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[list[Any], int]:
        qs = self.model_cls.all()

        if filters:
            for key, value in filters.items():
                qs = qs.filter(**{key: value})

        if search:
            if self.search_fields:
                search_qs = None
                for field in self.search_fields:
                    search_term = {field + "__icontains": search}
                    if search_qs is None:
                        search_qs = qs.filter(**search_term)
                    else:
                        search_qs |= qs.filter(**search_term)
                qs = search_qs.distinct()

        if sort_by:
            qs = qs.order_by(sort_by)
        else:
            if self.ordering:
                qs = qs.order_by(*self.ordering)

        total = await qs.count()

        if offset is not None and limit is not None:
            qs = qs.offset(offset)
            qs = qs.limit(limit)

        if self.list_select_related:
            qs = qs.select_related(*self.list_select_related)

        return await qs, total

    async def get_fields(self) -> Sequence[str]:
        fields = await super().get_fields()
        model_fields = self._get_model_fields()
        if not fields:
            if self.exclude:
                return (f for f in model_fields if f not in self.exclude)
            return model_fields
        return (f for f in fields if f in model_fields)

    async def get_list_display(self) -> Sequence[str]:
        list_display = await super().get_list_display()
        model_fields = self._get_model_fields()
        if not list_display:
            return (f for f in model_fields if getattr(model_fields[f], "index", False))
        return (f for f in list_display if f in model_fields)

    async def get_hidden_fields(self) -> Sequence[str]:
        hidden_fields = await super().get_hidden_fields()
        model_fields = self._get_model_fields()
        if not hidden_fields:
            return (
                f
                for f in model_fields
                if (
                    model_fields[f].__class__.__name__ == "BackwardFKRelation"
                    or getattr(model_fields[f], "index", False)
                    or getattr(model_fields[f], "auto_now", False)
                    or getattr(model_fields[f], "auto_now_add", False)
                    or getattr(model_fields[f], "_generated", False)
                )
                and f not in self.readonly_fields
            )
        return (f for f in hidden_fields if f in model_fields)

    async def get_form_widget(self, field: str) -> tuple[WidgetType, WidgetType]:
        field_obj = self.model_cls._meta.fields_map[field]
        widget_props = {
            "required": not field_obj.null and not field_obj.default,
            "disabled": field in self.readonly_fields,
        }
        field_class = field_obj.__class__.__name__

        if field_class == "CharField":
            return WidgetType.Input, widget_props
        if field_class == "TextField":
            return WidgetType.TextArea, widget_props
        if field_class == "BooleanField":
            return WidgetType.Switch, {**widget_props, "required": False}
        if field_class == "ArrayField":
            return WidgetType.Select, {
                **widget_props,
                "mode": "tags",
            }
        if field_class == "IntField":
            return WidgetType.InputNumber, widget_props
        if field_class == "FloatField":
            return WidgetType.InputNumber, widget_props
        if field_class == "DecimalField":
            return WidgetType.InputNumber, widget_props
        if field_class == "DateField":
            return WidgetType.DatePicker, widget_props
        if field_class == "DatetimeField":
            return WidgetType.DateTimePicker, widget_props
        if field_class == "TimeField":
            return WidgetType.TimePicker, widget_props
        if field_class == "ForeignKeyFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            return WidgetType.AsyncSelect, {
                **widget_props,
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "username",
            }
        if field_class == "ManyToManyFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            return WidgetType.AsyncSelect, {
                **widget_props,
                "required": False,
                "mode": "multiple",
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "username",
            }
        if field_class == "OneToOneFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            return WidgetType.AsyncSelect, {
                **widget_props,
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "username",
            }
        if field_class == "CharEnumFieldInstance":
            return WidgetType.RadioGroup if field in self.radio_fields else WidgetType.Select, {
                **widget_props,
                "options": [{"label": k, "value": k} for k in field_obj.enum_type],
            }
        return WidgetType.Input, widget_props

    async def get_filter_widget(self, field: str) -> tuple[WidgetType, WidgetType]:
        field_obj = self.model_cls._meta.fields_map[field]
        widget_props = {}
        field_class = field_obj.__class__.__name__
        if field_class == "CharField":
            return WidgetType.Input, widget_props
        if field_class == "TextField":
            return WidgetType.Input, widget_props
        if field_class == "BooleanField":
            return WidgetType.RadioGroup, {
                **widget_props,
                "options": [
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
            }
        if field_class == "ArrayField":
            return WidgetType.Select, {
                **widget_props,
                "mode": "tags",
            }
        if field_class == "IntField":
            return WidgetType.InputNumber, widget_props
        if field_class == "FloatField":
            return WidgetType.InputNumber, widget_props
        if field_class == "DecimalField":
            return WidgetType.InputNumber, widget_props
        if field_class == "DateField":
            return WidgetType.RangePicker, widget_props
        if field_class == "DatetimeField":
            return WidgetType.RangePicker, widget_props
        if field_class == "TimeField":
            return WidgetType.RangePicker, widget_props
        if field_class == "ForeignKeyFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            return WidgetType.AsyncSelect, {
                **widget_props,
                "mode": "multiple",
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "id",  # TODO: labelField
            }
        if field_class == "ManyToManyFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            return WidgetType.AsyncSelect, {
                **widget_props,
                "mode": "multiple",
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "id",  # TODO: labelField
            }
        if field_class == "OneToOneFieldInstance":
            if field in self.raw_id_fields:
                return WidgetType.Input, widget_props
            return WidgetType.AsyncSelect, {
                **widget_props,
                "mode": "multiple",
                "parentModel": field_obj.model_name.rsplit(".", 1)[-1],
                "idField": "id",
                "labelField": "id",  # TODO: labelField
            }
        if field_class == "CharEnumFieldInstance":
            return WidgetType.Select, {
                **widget_props,
                "mode": "multiple",
                "options": [{"label": k, "value": k} for k in field_obj.enum_type],
            }
        return WidgetType.Input, widget_props


def register_admin_model(admin_model_class: type[ModelAdmin], model_classes: list[Any]):
    from fastapi_admin.main import admin_models

    for model_class in model_classes:
        admin_models[model_class] = admin_model_class


def get_admin_models() -> dict[Any, type[ModelAdmin]]:
    from fastapi_admin.main import admin_models

    return admin_models


def get_admin_model(model_name: str) -> ModelAdmin | None:
    from fastapi_admin.main import admin_models

    for model, admin_model in admin_models.items():
        if model.__name__ == model_name:
            return admin_model(model)
    return None
