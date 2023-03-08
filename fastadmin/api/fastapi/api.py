import inspect
import logging
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any, cast
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse

from fastadmin.api.fastapi.depends import get_user_id, get_user_id_or_none
from fastadmin.api.helpers import generate_models_schema, sanitize
from fastadmin.api.schemas import ActionSchema, ExportSchema, SignInInputSchema
from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.helpers import get_admin_model, get_admin_model_classes
from fastadmin.models.schemas import ConfigurationSchema, ModelSchema
from fastadmin.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.post("/sign-in")
async def sign_in(
    response: Response,
    payload: SignInInputSchema,
) -> None:
    """This method is used to sign in.

    :params response: a response object.
    :params payload: a payload object.
    :return: None.
    """
    model = settings.ADMIN_USER_MODEL
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=f"{model} model is not registered.")

    user_id = await admin_model.authenticate(payload.username, payload.password)
    if not user_id or not (isinstance(user_id, int) or isinstance(user_id, UUID)):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    now = datetime.utcnow()
    session_expired_at = now + timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
    session_id = jwt.encode(
        {
            "user_id": str(user_id),
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
    _: UUID | int = Depends(get_user_id),
) -> None:
    """This method is used to sign out.

    :params response: a response object.
    :return: None.
    """
    response.delete_cookie(settings.ADMIN_SESSION_ID_KEY)
    return None


@router.get("/me")
async def me(
    user_id: UUID | int = Depends(get_user_id),
) -> Any:
    """This method is used to get current user.

    :params user_id: a user id.
    :return: A user object.
    """
    model = settings.ADMIN_USER_MODEL
    admin_model: Any = get_admin_model(model)
    return await admin_model.get_obj(user_id)


@router.get("/list/{model}")
async def list(
    request: Request,
    model: str,
    search: str | None = None,
    sort_by: str = None,
    offset: int | None = 0,
    limit: int | None = 10,
    _: UUID | int = Depends(get_user_id),
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
    id: UUID | int,
    _: UUID | int = Depends(get_user_id),
) -> Any:
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
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} not found.")
    return obj


@router.post("/add/{model}")
async def add(
    model: str,
    payload: dict,
    _: UUID | int = Depends(get_user_id),
) -> Any:
    """This method is used to add an object.

    :params model: a name of model.
    :params payload: a payload object.
    :return: An object.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    return await admin_model.save_model(None, payload)


@router.patch("/change/{model}/{id}")
async def change(
    model: str,
    id: UUID | int,
    payload: dict,
    _: UUID | int = Depends(get_user_id),
) -> Any:
    """This method is used to change an object.

    :params model: a name of model.
    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    obj = await admin_model.save_model(id, payload)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} not found.")
    return obj


@router.post("/export/{model}")
async def export(
    request: Request,
    model: str,
    payload: ExportSchema,
    search: str | None = None,
    sort_by: str = None,
    _: UUID | int = Depends(get_user_id),
):
    """This method is used to export a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params payload: a payload object.
    :params search: a search string.
    :params sort_by: a sort by string.
    :return: A stream of export data.
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
    id: UUID | int,
    user_id: UUID | int = Depends(get_user_id),
) -> UUID | int:
    """This method is used to delete an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An id of object.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")
    if str(user_id) == str(id) and model == settings.ADMIN_USER_MODEL:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You cannot delete yourself.")
    await admin_model.delete_model(id)
    return id


@router.post("/action/{model}/{action}")
async def action(
    request: Request,
    model: str,
    action: str,
    payload: ActionSchema,
    _: UUID | int = Depends(get_user_id),
) -> None:
    """This method is used to perform an action.

    :params request: a request object.
    :params model: a name of model.
    :params action: a name of action.
    :params payload: a payload object.
    :return: A list of objects.
    """
    admin_model = get_admin_model(model)
    if not admin_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"{model} model is not registered.")

    if action not in admin_model.actions:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{action} action is not in actions setting.")

    action_function = getattr(admin_model, action, None)
    if not action_function or not inspect.ismethod(action_function) or not hasattr(action_function, "is_action"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{action} action is not registered.")

    await action_function(payload.ids)


@router.get("/configuration")
async def configuration(
    user_id: UUID | int | None = Depends(get_user_id_or_none),
) -> ConfigurationSchema:
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

    admin_models = cast(dict[Any, type[ModelAdmin | InlineModelAdmin]], get_admin_model_classes())
    models = cast(Sequence[ModelSchema], generate_models_schema(admin_models))
    return ConfigurationSchema(
        site_name=settings.ADMIN_SITE_NAME,
        site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
        site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
        site_favicon=settings.ADMIN_SITE_FAVICON,
        primary_color=settings.ADMIN_PRIMARY_COLOR,
        username_field=settings.ADMIN_USER_MODEL_USERNAME_FIELD,
        date_format=settings.ADMIN_DATE_FORMAT,
        datetime_format=settings.ADMIN_DATETIME_FORMAT,
        models=models,
    )
