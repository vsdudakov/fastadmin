from operator import attrgetter
from typing import Any, cast
from uuid import UUID

from fastadmin.models.base import InlineModelAdmin, ModelAdmin, admin_dashboard_widgets, admin_models
from fastadmin.models.schemas import (
    AddConfigurationFieldSchema,
    ChangeConfigurationFieldSchema,
    DashboardWidgetSchema,
    InlineModelSchema,
    ListConfigurationFieldSchema,
    ModelAction,
    ModelFieldSchema,
    ModelPermission,
    ModelSchema,
)


def register_admin_model_class(admin_model_class: type[ModelAdmin], orm_model_classes: list[Any], **kwargs) -> None:
    """This method is used to register an admin model.

    :params admin_model_class: a class of admin model.
    :params orm_model_classes: a list of orm model classes.
    :return: None.
    """
    for orm_model_class in orm_model_classes:
        sqlalchemy_sessionmaker = kwargs.get("sqlalchemy_sessionmaker")
        if sqlalchemy_sessionmaker:
            admin_model_class.set_sessionmaker(sqlalchemy_sessionmaker)
        admin_models[orm_model_class] = admin_model_class(orm_model_class)


def unregister_admin_model_class(orm_model_classes: list[Any]) -> None:
    """This method is used to unregister an admin model.

    :params orm_model_classes: a list of orm model classes.
    :return: None.
    """
    for orm_model_class in orm_model_classes:
        if orm_model_class in admin_models:
            del admin_models[orm_model_class]


def get_admin_models() -> dict[Any, ModelAdmin]:
    """This method is used to get a dict of admin models.

    :return: A dict of admin models.
    """
    return admin_models


def get_admin_model(orm_model_cls: str | Any) -> ModelAdmin | None:
    """This method is used to get an admin model class by orm model class name.

    :params orm_model_cls_name: a name of model.
    :return: An admin model class or None.
    """
    if not isinstance(orm_model_cls, str):
        return admin_models.get(orm_model_cls, None)
    for admin_model_orm_model_cls, admin_model in admin_models.items():
        model_name = admin_model_orm_model_cls.__name__
        model_name_prefix = admin_model.model_name_prefix
        if model_name_prefix:
            model_name = f"{model_name_prefix}.{model_name}"
        if orm_model_cls in model_name:
            return admin_model
    return None


def get_admin_or_admin_inline_model(orm_model_cls: str) -> ModelAdmin | InlineModelAdmin | None:
    """This method is used to get an admin model class or an inline model class by orm model class name.

    :params orm_model_cls_name: a name of model.
    :return: An admin model class or an inline model class or None.
    """
    if orm_model_cls.startswith("inlines."):
        orm_model_cls = orm_model_cls.replace("inlines.", "")
        for _, admin_model in admin_models.items():
            for inline_model in admin_model.inlines:
                if inline_model.model.__name__ == orm_model_cls:
                    return inline_model(inline_model.model)
        return None

    admin_model = get_admin_model(orm_model_cls)
    if admin_model:
        return admin_model
    return None


def generate_models_schema(
    admin_models: dict[Any, ModelAdmin | InlineModelAdmin],
    user_id: UUID | int | None = None,
    inline_parent_admin_modal: ModelAdmin | None = None,
) -> list[ModelSchema | InlineModelSchema]:
    """Generate models schema

    :params models: a dict of models.
    :params is_inline_models: a flag to indicate if models are inline models.
    :return: A list of models / inline models schemas.
    """
    models_schemas: list[ModelSchema | InlineModelSchema] = []
    for orm_model_cls in admin_models:
        admin_model_obj: ModelAdmin | InlineModelAdmin = admin_models[orm_model_cls]
        orm_model_fields = admin_model_obj.get_model_fields_with_widget_types()
        orm_model_fields_for_serialize = admin_model_obj.get_fields_for_serialize()

        column_fields = admin_model_obj.list_display or (admin_model_obj.get_model_pk_name(orm_model_cls),)
        form_fields = admin_model_obj.fields or [f.name for f in orm_model_fields if not f.is_immutable]

        fields_schema = []
        for orm_model_field in orm_model_fields:
            if orm_model_field.name not in orm_model_fields_for_serialize:
                continue

            field_name = orm_model_field.name
            column_index = column_fields.index(field_name) if field_name in column_fields else None

            list_configuration = None
            filter_widget_type = None
            filter_widget_props = None
            if column_index is not None and not orm_model_field.is_m2m:
                if field_name in admin_model_obj.list_filter:
                    filter_widget_type = orm_model_field.filter_widget_type
                    filter_widget_props = orm_model_field.filter_widget_props

                sorter = True
                if admin_model_obj.sortable_by and field_name not in admin_model_obj.sortable_by:
                    sorter = False

                list_configuration = ListConfigurationFieldSchema(
                    index=column_index,
                    sorter=sorter,
                    is_link=field_name in getattr(admin_model_obj, "list_display_links", []),
                    empty_value_display=admin_model_obj.empty_value_display,
                    filter_widget_type=filter_widget_type,
                    filter_widget_props=filter_widget_props,
                    width=admin_model_obj.list_display_widths.get(field_name, None),
                )

            add_configuration = None
            change_configuration = None
            if not orm_model_field.is_immutable:
                form_index = form_fields.index(field_name) if field_name in form_fields else None
                if form_index is not None:
                    form_widget_type = orm_model_field.form_widget_type
                    form_widget_props = orm_model_field.form_widget_props
                    add_configuration = AddConfigurationFieldSchema(
                        index=form_index,
                        form_widget_type=form_widget_type,
                        form_widget_props=form_widget_props,
                        required=form_widget_props.get("required", False),
                    )
                    change_configuration = ChangeConfigurationFieldSchema(
                        index=form_index,
                        form_widget_type=form_widget_type,
                        form_widget_props=form_widget_props,
                        required=form_widget_props.get("required", False),
                    )

            fields_schema.append(
                ModelFieldSchema(
                    name=field_name,
                    list_configuration=list_configuration,
                    add_configuration=add_configuration,
                    change_configuration=change_configuration,
                ),
            )

        for column_index, field_name in enumerate(orm_model_fields_for_serialize):
            display_field_function = getattr(admin_model_obj, field_name, None)
            if not display_field_function or not hasattr(display_field_function, "is_display"):
                continue

            fields_schema.append(
                ModelFieldSchema(
                    name=field_name,
                    list_configuration=ListConfigurationFieldSchema(
                        index=column_index,
                        sorter=False,
                        is_link=field_name in getattr(admin_model_obj, "list_display_links", ()),
                        empty_value_display=admin_model_obj.empty_value_display,
                        filter_widget_type=None,
                        filter_widget_props=None,
                        width=None,
                    ),
                    add_configuration=None,
                    change_configuration=None,
                ),
            )

        permissions = []
        if admin_model_obj.has_add_permission(user_id=user_id):
            permissions.append(ModelPermission.Add)
        if admin_model_obj.has_change_permission(user_id=user_id):
            permissions.append(ModelPermission.Change)
        if admin_model_obj.has_delete_permission(user_id=user_id):
            permissions.append(ModelPermission.Delete)
        if admin_model_obj.has_export_permission(user_id=user_id):
            permissions.append(ModelPermission.Export)

        actions = []
        for action in admin_model_obj.actions:
            action_function = getattr(admin_model_obj, action, None)
            if not action_function or not hasattr(action_function, "is_action"):
                continue
            actions.append(
                ModelAction(
                    name=action,
                    description=getattr(action_function, "short_description", None),
                )
            )

        model_name = orm_model_cls.__name__
        model_name_prefix = admin_model_obj.model_name_prefix
        if model_name_prefix:
            model_name = f"{model_name_prefix}.{model_name}"
        if not inline_parent_admin_modal:
            admin_model_obj = cast(ModelAdmin, admin_model_obj)
            models_schemas.append(
                ModelSchema(
                    name=model_name,
                    permissions=permissions,
                    actions=actions,
                    actions_on_top=admin_model_obj.actions_on_top,
                    actions_on_bottom=admin_model_obj.actions_on_bottom,
                    actions_selection_counter=admin_model_obj.actions_selection_counter,
                    fields=fields_schema,
                    list_per_page=admin_model_obj.list_per_page,
                    search_help_text=admin_model_obj.search_help_text,
                    search_fields=admin_model_obj.search_fields,
                    preserve_filters=admin_model_obj.preserve_filters,
                    list_max_show_all=admin_model_obj.list_max_show_all,
                    show_full_result_count=admin_model_obj.show_full_result_count,
                    verbose_name=admin_model_obj.verbose_name,
                    verbose_name_plural=admin_model_obj.verbose_name_plural,
                    # specific model fields
                    fieldsets=admin_model_obj.fieldsets,
                    save_on_top=admin_model_obj.save_on_top,
                    save_as=admin_model_obj.save_as,
                    save_as_continue=admin_model_obj.save_as_continue,
                    view_on_site=admin_model_obj.view_on_site,
                    inlines=generate_models_schema(
                        {inline.model: inline(inline.model) for inline in admin_model_obj.inlines},
                        inline_parent_admin_modal=admin_model_obj,
                        user_id=user_id,
                    ),  # type: ignore [arg-type]
                ),
            )
        else:
            admin_model_obj = cast(InlineModelAdmin, admin_model_obj)
            fk_name = admin_model_obj.fk_name
            if not fk_name:
                parent_model = inline_parent_admin_modal.model_cls.__name__
                fk_names = [f.name for f in orm_model_fields if f.form_widget_props.get("parentModel") == parent_model]
                if len(fk_names) != 1:
                    raise ValueError(
                        f"Couldn't auto-identify fk_name. Please specify fk_name for inline model {admin_model_obj}."
                    )
                fk_name = fk_names[0]

            models_schemas.append(
                InlineModelSchema(
                    name=model_name,
                    permissions=permissions,
                    actions=actions,
                    actions_on_top=admin_model_obj.actions_on_top,
                    actions_on_bottom=admin_model_obj.actions_on_bottom,
                    actions_selection_counter=admin_model_obj.actions_selection_counter,
                    fields=fields_schema,
                    list_per_page=admin_model_obj.list_per_page,
                    search_help_text=admin_model_obj.search_help_text,
                    search_fields=admin_model_obj.search_fields,
                    preserve_filters=admin_model_obj.preserve_filters,
                    list_max_show_all=admin_model_obj.list_max_show_all,
                    show_full_result_count=admin_model_obj.show_full_result_count,
                    verbose_name=admin_model_obj.verbose_name,
                    verbose_name_plural=admin_model_obj.verbose_name_plural,
                    # specific inline model fields
                    fk_name=fk_name,
                    max_num=admin_model_obj.max_num,
                    min_num=admin_model_obj.min_num,
                ),
            )
    return models_schemas


def generate_dashboard_widgets_schema() -> list[DashboardWidgetSchema]:
    """Generate dashboard widgets schema."""
    dashboard_widgets_schemas: list[DashboardWidgetSchema] = []
    for admin_dashboard_widget in admin_dashboard_widgets.values():
        dashboard_widgets_schemas.append(
            DashboardWidgetSchema(
                key=admin_dashboard_widget.__class__.__name__,
                title=admin_dashboard_widget.title,
                dashboard_widget_type=admin_dashboard_widget.dashboard_widget_type,
                x_field=admin_dashboard_widget.x_field,
                y_field=admin_dashboard_widget.y_field,
                series_field=admin_dashboard_widget.series_field,
                x_field_filter_widget_type=admin_dashboard_widget.x_field_filter_widget_type,
                x_field_filter_widget_props=admin_dashboard_widget.x_field_filter_widget_props,
                x_field_periods=admin_dashboard_widget.x_field_periods,
            ),
        )
    return dashboard_widgets_schemas


def getattrs(obj: Any, attrs: str, default: Any | None = None) -> Any:
    """Get attributes from an object.

    :param obj: An object.
    :param attrs: A string of attributes separated by dots.
    :param default: A default value to return if an attribute is not found.
    :return: The value of the last attribute.
    """
    try:
        return attrgetter(attrs)(obj)
    except (TypeError, AttributeError):
        return default
