import logging
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse

from fastadmin.api.depends import get_user_id, get_user_id_or_none
from fastadmin.api.helpers import sanitize
from fastadmin.models.base import BaseModelAdmin
from fastadmin.models.helpers import get_admin_model, get_admin_models
from fastadmin.schemas.api import ExportSchema, SignInInputSchema
from fastadmin.schemas.configuration import (
    AddConfigurationFieldSchema,
    ChangeConfigurationFieldSchema,
    ConfigurationSchema,
    ListConfigurationFieldSchema,
    ModelFieldSchema,
    ModelPermission,
    ModelSchema,
)
from fastadmin.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.post("/sign-in")
async def sign_in(
    response: Response,
    payload: SignInInputSchema,
):
    """This method is used to sign in.

    :params response: a response object.
    :params payload: a payload object.
    :return: None.
    """
    model = settings.ADMIN_USER_MODEL
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=f"{model} model is not registered.")

    user = await admin_model.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    now = datetime.utcnow()
    session_expired_at = now + timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
    session_id = jwt.encode(
        {
            "user_id": str(user.id),
            "session_expired_at": session_expired_at.isoformat(),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    response.set_cookie(settings.ADMIN_SESSION_ID_KEY, value=session_id, httponly=True)
    return None


@router.post("/sign-out")
async def sign_out(
    response: Response,
    _: str = Depends(get_user_id),
):
    """This method is used to sign out.

    :params response: a response object.
    :return: None.
    """
    response.delete_cookie(settings.ADMIN_SESSION_ID_KEY)
    return None


@router.get("/me")
async def me(
    user_id: str = Depends(get_user_id),
):
    """This method is used to get current user.

    :params user_id: a user id.
    :return: A user object.
    """
    model = settings.ADMIN_USER_MODEL
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    user = await admin_model.get_obj(user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.get("/list/{model}")
async def list(
    request: Request,
    model: str,
    search: str | None = None,
    sort_by: str = "-created_at",
    offset: int | None = 0,
    limit: int | None = 10,
    _: str = Depends(get_user_id),
):
    """This method is used to get a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params search: a search string.
    :params sort_by: a sort by string.
    :params offset: an offset.
    :params limit: a limit.
    :return: A list of objects.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")

    filters = {
        k: sanitize(v)
        for k, v in request.query_params._dict.items()
        if k not in ("search", "sort_by", "offset", "limit")
    }
    objs, total = await admin_model.get_list(
        offset=offset,
        limit=limit,
        search=search,
        sort_by=sort_by,
        filters=filters,
    )
    return {
        "total": total,
        "results": objs,
    }


@router.get("/retrieve/{model}/{id}")
async def get(
    model: str,
    id: str,
    _: str = Depends(get_user_id),
):
    """This method is used to get an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An object.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    obj = await admin_model.get_obj(id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    return obj


@router.post("/add/{model}")
async def add(
    model: str,
    payload: dict,
    _: str = Depends(get_user_id),
):
    """This method is used to add an object.

    :params model: a name of model.
    :params payload: a payload object.
    :return: An object.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    obj = admin_model.model_cls()
    await admin_model.save_model(obj, payload, add=True)
    return obj


@router.patch("/change/{model}/{id}")
async def change(
    model: str,
    id: str,
    payload: dict,
    _: str = Depends(get_user_id),
):
    """This method is used to change an object.

    :params model: a name of model.
    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    obj = await admin_model.get_obj(id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    await admin_model.save_model(obj, payload)
    return obj


@router.post("/export/{model}")
async def export(
    request: Request,
    model: str,
    payload: ExportSchema,
    search: str | None = None,
    sort_by: str = "-created_at",
    _: str = Depends(get_user_id),
):
    """This method is used to export a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params payload: a payload object.
    :params search: a search string.
    :params sort_by: a sort by string.
    :return: A list of objects.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")

    filters = {k: v for k, v in request.query_params._dict.items() if k not in ("search", "sort_by")}
    file_name = f"{model}.{(payload.format or 'csv').lower()}"
    headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}
    stream = await admin_model.get_export(
        payload.format,
        search=search,
        sort_by=sort_by,
        filters=filters,
        offset=payload.offset,
        limit=payload.limit,
    )
    return StreamingResponse(
        stream,  # type: ignore
        headers=headers,
        media_type="text/csv",
    )


@router.delete("/delete/{model}/{id}")
async def delete(
    model: str,
    id: str,
    user_id: str = Depends(get_user_id),
):
    """This method is used to delete an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An object.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    if user_id == id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You cannot delete yourself.")
    user = await admin_model.get_obj(id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    await admin_model.delete_model(user)
    return user


@router.get("/configuration")
async def configuration(
    user_id: str | None = Depends(get_user_id_or_none),
):
    """This method is used to get a configuration.

    :params user_id: an id of user.
    :return: A configuration.
    """
    if not user_id:
        return ConfigurationSchema(
            site_name=settings.ADMIN_SITE_NAME,
            site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
            site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
            site_favicon=settings.ADMIN_SITE_FAVICON,
            primary_color=settings.ADMIN_PRIMARY_COLOR,
            username_field=settings.ADMIN_USER_MODEL_USERNAME_FIELD,
            date_format=settings.ADMIN_DATE_FORMAT,
            datetime_format=settings.ADMIN_DATETIME_FORMAT,
            models=[],
        )

    models = get_admin_models()
    models_schemas = []
    for model_cls in models:
        admin_obj: BaseModelAdmin = models[model_cls](model_cls)

        model_fields = admin_obj.get_model_fields()

        fields_schema = []
        for field_name, field in model_fields.items():
            list_display = admin_obj.get_list_display()
            column_index = list_display.index(field_name) if field_name in list_display else None
            list_configuration = None
            filter_widget_type = None
            filter_widget_props = None
            if column_index is not None:
                if field_name in admin_obj.list_filter:
                    filter_widget_type, filter_widget_props = admin_obj.get_filter_widget(field_name)
                sorter = True
                if admin_obj.sortable_by and field_name not in admin_obj.sortable_by:
                    sorter = False
                list_configuration = ListConfigurationFieldSchema(
                    index=column_index,
                    sorter=sorter,
                    is_link=field_name in admin_obj.list_display_links,
                    empty_value_display=admin_obj.empty_value_display,
                    filter_widget_type=filter_widget_type,
                    filter_widget_props=filter_widget_props,
                )

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

        permissions = []
        if admin_obj.has_add_permission():
            permissions.append(ModelPermission.Add)
        if admin_obj.has_change_permission():
            permissions.append(ModelPermission.Change)
        if admin_obj.has_delete_permission():
            permissions.append(ModelPermission.Delete)
        if admin_obj.has_export_permission():
            permissions.append(ModelPermission.Export)

        models_schemas.append(
            ModelSchema(
                name=model_cls.__name__,
                permissions=permissions,
                fields=fields_schema,
                list_per_page=admin_obj.list_per_page,
                save_on_top=admin_obj.save_on_top,
                save_as=admin_obj.save_as,
                save_as_continue=admin_obj.save_as_continue,
                view_on_site=admin_obj.view_on_site,
                search_help_text=admin_obj.search_help_text,
                search_fields=admin_obj.search_fields,
                preserve_filters=admin_obj.preserve_filters,
                list_max_show_all=admin_obj.list_max_show_all,
                show_full_result_count=admin_obj.show_full_result_count,
            ),
        )

    return ConfigurationSchema(
        site_name=settings.ADMIN_SITE_NAME,
        site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
        site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
        site_favicon=settings.ADMIN_SITE_FAVICON,
        primary_color=settings.ADMIN_PRIMARY_COLOR,
        username_field=settings.ADMIN_USER_MODEL_USERNAME_FIELD,
        date_format=settings.ADMIN_DATE_FORMAT,
        datetime_format=settings.ADMIN_DATETIME_FORMAT,
        models=models_schemas,
    )
