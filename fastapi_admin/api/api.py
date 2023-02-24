import logging
from datetime import datetime, timedelta
from io import StringIO

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse

from fastapi_admin.api.depends import get_user_id, get_user_id_or_none
from fastapi_admin.api.schemas.api import ExportSchema, SignInInputSchema
from fastapi_admin.api.schemas.configuration import (
    AddConfigurationFieldSchema,
    ChangeConfigurationFieldSchema,
    ConfigurationSchema,
    ListConfigurationFieldSchema,
    ModelFieldSchema,
    ModelPermission,
    ModelSchema,
)
from fastapi_admin.models import ModelAdmin, get_admin_model, get_admin_models
from fastapi_admin.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.post("/sign-in")
async def sign_in(
    request: Request,
    response: Response,
    payload: SignInInputSchema,
):
    model = settings.ADMIN_USER_MODEL
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=f"{model} model is not registered.")

    users, _ = await admin_model.get_list(filters={settings.ADMIN_USER_MODEL_USERNAME_FIELD: payload.username})
    if not users:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    user = users[0]

    if not hasattr(user, "check_password"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User model must have check_password method.")

    if not user.check_password(payload.password):
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
    response.delete_cookie(settings.ADMIN_SESSION_ID_KEY)
    return None


@router.get("/me")
async def me(
    user_id: str = Depends(get_user_id),
):
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
    response: Response,
    model: str,
    search: str | None = None,
    sort_by: str = "-created_at",
    offset: int | None = 0,
    limit: int | None = 10,
    _: str = Depends(get_user_id),
):
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")

    filters = {k: v for k, v in request.query_params._dict.items() if k not in ("search", "sort_by", "offset", "limit")}
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
    request: Request,
    model: str,
    id: str,
    _: str = Depends(get_user_id),
):
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
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    obj = admin_model.model_cls()
    await admin_model.save_model(obj, payload.dict())
    return obj


@router.patch("/change/{model}/{id}")
async def change(
    model: str,
    id: str,
    payload: dict,
    _: str = Depends(get_user_id),
):
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    obj = await admin_model.get_obj(id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    await admin_model.save_model(obj, payload.dict())
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
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")

    filters = {k: v for k, v in request.query_params._dict.items() if k not in ("search", "sort_by")}
    objs, _ = await admin_model.get_list(
        search=search,
        sort_by=sort_by,
        filters=filters,
    )
    file_name = f"{model}.csv"
    csv = "test,test\n1,2"
    headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}
    return StreamingResponse(
        StringIO(csv),
        headers=headers,
        media_type="text/csv",
    )


@router.delete("/delete/{model}/{id}")
async def delete(
    request: Request,
    response: Response,
    model: str,
    id: str,
    _: str = Depends(get_user_id),
):
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    user = await admin_model.get_obj(id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    await admin_model.delete_obj(user)
    return user


@router.get("/configuration")
async def configuration(
    request: Request,
    user_id: str | None = Depends(get_user_id_or_none),
):
    if not user_id:
        return ConfigurationSchema(
            site_name=settings.ADMIN_SITE_NAME,
            site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
            site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
            site_favicon=settings.ADMIN_SITE_FAVICON,
            primary_color=settings.ADMIN_PRIMARY_COLOR,
            username_field=settings.ADMIN_USER_MODEL_USERNAME_FIELD,
            models=[],
        )

    models = get_admin_models()
    models_schemas = []
    for model_cls in models:
        admin_obj: ModelAdmin = models[model_cls](model_cls)

        fields = await admin_obj.get_fields()
        fields_schema = []
        for field_name in fields:
            form_widget_type, form_widget_props = await admin_obj.get_form_widget(field_name)
            readonly_fields = await admin_obj.get_readonly_fields()

            list_display = await admin_obj.get_list_display()
            list_configuration = None
            filter_widget_type = None
            filter_widget_props = None
            if field_name in list_display:
                if field_name in admin_obj.list_filter:
                    filter_widget_type, filter_widget_props = await admin_obj.get_filter_widget(field_name)
                sorter = True
                if admin_obj.sortable_by and field_name not in admin_obj.sortable_by:
                    sorter = False
                list_configuration = ListConfigurationFieldSchema(
                    sorter=sorter,
                    is_link=field_name in admin_obj.list_display_links,
                    empty_value_display=admin_obj.empty_value_display,
                    filter_widget_type=filter_widget_type,
                    filter_widget_props=filter_widget_props,
                )

            add_configuration = None
            if field_name not in readonly_fields:
                add_configuration = AddConfigurationFieldSchema(
                    form_widget_type=form_widget_type,
                    form_widget_props=form_widget_props,
                    required=form_widget_props.get("required", False),
                )

            change_configuration = None
            if field_name not in readonly_fields:
                change_configuration = ChangeConfigurationFieldSchema(
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
        if await admin_obj.has_add_permission():
            permissions.append(ModelPermission.Add)
        if await admin_obj.has_change_permission():
            permissions.append(ModelPermission.Change)
        if await admin_obj.has_delete_permission():
            permissions.append(ModelPermission.Delete)
        if await admin_obj.has_export_permission():
            permissions.append(ModelPermission.Export)

        models_schemas.append(
            ModelSchema(
                name=model_cls.__name__,
                permissions=permissions,
                fields=fields_schema,
                list_per_page=admin_obj.list_per_page,
                save_on_top=admin_obj.save_on_top,
                search_help_text=admin_obj.search_help_text,
            ),
        )

    return ConfigurationSchema(
        site_name=settings.ADMIN_SITE_NAME,
        site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
        site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
        site_favicon=settings.ADMIN_SITE_FAVICON,
        primary_color=settings.ADMIN_PRIMARY_COLOR,
        username_field=settings.ADMIN_USER_MODEL_USERNAME_FIELD,
        models=models_schemas,
    )
