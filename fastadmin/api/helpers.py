import inspect
from datetime import datetime
from typing import Any, cast
from uuid import UUID

import jwt

from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.helpers import get_admin_model
from fastadmin.models.schemas import (
    AddConfigurationFieldSchema,
    ChangeConfigurationFieldSchema,
    InlineModelSchema,
    ListConfigurationFieldSchema,
    ModelAction,
    ModelFieldSchema,
    ModelPermission,
    ModelSchema,
)
from fastadmin.settings import settings


def sanitize(value: str) -> bool | None | str:
    """Sanitize value

    :params value: a value.
    :return: A sanitized value.
    """
    if value == "false":
        return False
    elif value == "true":
        return True
    elif value == "null":
        return None
    return value


def is_valid_uuid(uuid_to_test: str) -> bool:
    """Check if uuid_to_test is a valid uuid.

    :param uuid_to_test: A uuid to test.
    :return: True if uuid_to_test is a valid uuid, False otherwise.
    """
    try:
        uuid_obj = UUID(uuid_to_test)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def is_digit(digit_to_test: str) -> bool:
    """Check if digit_to_test is a digit.

    :param digit_to_test: A digit to test.
    :return: True if digit_to_test is a digit, False otherwise.
    """
    try:
        int(digit_to_test)
    except ValueError:
        return False
    return True


async def get_user_id_from_session_id(session_id: str | None) -> UUID | int | None:
    """This method is used to get user id from session_id.

    :param session_id: A session id.
    :return: A user id or None.
    """
    if not session_id:
        return None

    admin_model = get_admin_model(settings.ADMIN_USER_MODEL)
    if not admin_model:
        return None

    try:
        token_payload = jwt.decode(session_id, settings.ADMIN_SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

    session_expired_at = token_payload.get("session_expired_at")
    if not session_expired_at:
        return None

    if datetime.fromisoformat(session_expired_at) < datetime.utcnow():
        return None

    user_id = token_payload.get("user_id")

    if not user_id or not await admin_model.get_obj(user_id):
        return None

    return user_id


def generate_models_schema(
    admin_models: dict[Any, ModelAdmin | InlineModelAdmin],
    is_inline_models: bool = False,
) -> list[ModelSchema | InlineModelSchema]:
    """Generate models schema

    :params models: a dict of models.
    :return: A list of models schema.
    """
    models_schemas: list[ModelSchema | InlineModelSchema] = []
    for orm_model_cls in admin_models:
        admin_obj: ModelAdmin | InlineModelAdmin = admin_models[orm_model_cls]

        model_fields = admin_obj.get_model_fields()
        list_display = admin_obj.get_list_display()

        fields_schema = []
        display_fields = []
        for field_name, field in model_fields.items():
            is_m2m = model_fields.get(field_name, {}).get("is_m2m")
            column_index = list_display.index(field_name) if field_name in list_display else None
            list_configuration = None
            filter_widget_type = None
            filter_widget_props = None
            if column_index is not None and not is_m2m:
                if field_name in admin_obj.list_filter:
                    filter_widget_type, filter_widget_props = admin_obj.get_filter_widget(field_name)
                sorter = True
                if admin_obj.sortable_by and field_name not in admin_obj.sortable_by:
                    sorter = False
                list_configuration = ListConfigurationFieldSchema(
                    index=column_index,
                    sorter=sorter,
                    is_link=field_name in getattr(admin_obj, "list_display_links", []),
                    empty_value_display=admin_obj.empty_value_display,
                    filter_widget_type=filter_widget_type,
                    filter_widget_props=filter_widget_props,
                )
            else:
                display_fields.append(field_name)

            add_configuration = None
            change_configuration = None
            if not field.get("form_hidden"):
                fields = admin_obj.get_fields()
                form_index = fields.index(field_name) if field_name in fields else None
                if form_index is not None:
                    form_widget_type, form_widget_props = admin_obj.get_form_widget(field_name)
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

        for column_index, field_name in enumerate(admin_obj.list_display):
            display_field_function = getattr(admin_obj, field_name, None)
            if (
                not display_field_function
                or not inspect.ismethod(display_field_function)
                or not hasattr(display_field_function, "is_display")
            ):
                continue

            fields_schema.append(
                ModelFieldSchema(
                    name=field_name,
                    list_configuration=ListConfigurationFieldSchema(
                        index=column_index,
                        sorter=False,
                        is_link=field_name in getattr(admin_obj, "list_display_links", ()),
                        empty_value_display=admin_obj.empty_value_display,
                        filter_widget_type=None,
                        filter_widget_props=None,
                    ),
                    add_configuration=None,
                    change_configuration=None,
                ),
            )

        permissions = []
        if admin_obj.has_add_permission():
            permissions.append(ModelPermission.Add)
        if admin_obj.has_change_permission():
            permissions.append(ModelPermission.Change)
        if admin_obj.has_delete_permission():
            permissions.append(ModelPermission.Delete)
        if admin_obj.has_export_permission():
            permissions.append(ModelPermission.Export)

        actions = []
        for action in admin_obj.actions:
            action_function = getattr(admin_obj, action, None)
            if (
                not action_function
                or not inspect.ismethod(action_function)
                or not hasattr(action_function, "is_action")
            ):
                continue
            actions.append(
                ModelAction(
                    name=action,
                    description=getattr(action_function, "short_description", None),
                )
            )

        if not is_inline_models:
            admin_obj = cast(ModelAdmin, admin_obj)
            models_schemas.append(
                ModelSchema(
                    name=orm_model_cls.__name__,
                    permissions=permissions,
                    actions=actions,
                    actions_on_top=admin_obj.actions_on_top,
                    actions_on_bottom=admin_obj.actions_on_bottom,
                    actions_selection_counter=admin_obj.actions_selection_counter,
                    fields=fields_schema,
                    list_per_page=admin_obj.list_per_page,
                    search_help_text=admin_obj.search_help_text,
                    search_fields=admin_obj.search_fields,
                    preserve_filters=admin_obj.preserve_filters,
                    list_max_show_all=admin_obj.list_max_show_all,
                    show_full_result_count=admin_obj.show_full_result_count,
                    # specific model fields
                    fieldsets=admin_obj.fieldsets,
                    save_on_top=admin_obj.save_on_top,
                    save_as=admin_obj.save_as,
                    save_as_continue=admin_obj.save_as_continue,
                    view_on_site=admin_obj.view_on_site,
                    inlines=generate_models_schema(
                        {inline.model: inline(inline.model) for inline in admin_obj.inlines}, is_inline_models=True
                    ),
                ),
            )
        else:
            admin_obj = cast(InlineModelAdmin, admin_obj)
            models_schemas.append(
                InlineModelSchema(
                    name=orm_model_cls.__name__,
                    permissions=permissions,
                    actions=actions,
                    actions_on_top=admin_obj.actions_on_top,
                    actions_on_bottom=admin_obj.actions_on_bottom,
                    actions_selection_counter=admin_obj.actions_selection_counter,
                    fields=fields_schema,
                    list_per_page=admin_obj.list_per_page,
                    search_help_text=admin_obj.search_help_text,
                    search_fields=admin_obj.search_fields,
                    preserve_filters=admin_obj.preserve_filters,
                    list_max_show_all=admin_obj.list_max_show_all,
                    show_full_result_count=admin_obj.show_full_result_count,
                    # specific inline model fields
                    fk_name=admin_obj.fk_name,
                    max_num=admin_obj.max_num,
                    min_num=admin_obj.min_num,
                    verbose_name=admin_obj.verbose_name,
                    verbose_name_plural=admin_obj.verbose_name_plural,
                ),
            )
    return models_schemas
