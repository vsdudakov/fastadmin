import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, StreamingResponse

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.schemas import ActionInputSchema, ExportInputSchema, SignInInputSchema
from fastadmin.api.service import ApiService, get_user_id_from_session_id
from fastadmin.models.schemas import ConfigurationSchema
from fastadmin.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
api_service = ApiService()


@router.post("/sign-in")
async def sign_in(
    request: Request,
    response: Response,
    payload: SignInInputSchema,
) -> None:
    """This method is used to sign in.

    :params request: a request object.
    :params response: a response object.
    :params payload: a payload object.
    :return: None.
    """

    try:
        session_id = await api_service.sign_in(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            payload,
        )

        response.set_cookie(settings.ADMIN_SESSION_ID_KEY, value=session_id, httponly=True)
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.post("/sign-out")
async def sign_out(
    request: Request,
    response: Response,
) -> None:
    """This method is used to sign out.

    :params request: a request object.
    :params response: a response object.
    :return: None.
    """
    try:
        if await api_service.sign_out(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
        ):
            response.delete_cookie(settings.ADMIN_SESSION_ID_KEY)
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.get("/me")
async def me(
    request: Request,
) -> Any:
    """This method is used to get current user.

    :params user_id: a user id.
    :return: A user object.
    """
    try:
        user_id = await get_user_id_from_session_id(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
        )
        if not user_id:
            raise AdminApiException(401, "User is not authenticated.")
        return await api_service.get(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None), settings.ADMIN_USER_MODEL, user_id
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.get("/dashboard-widget/{model}")
async def dashboard_widget(
    request: Request,
    model: str,
    min_x_field: str | None = None,
    max_x_field: str | None = None,
    period_x_field: str | None = None,
):
    """This method is used to get a dashboard widget data.

    :params model: a dashboard widget model.
    :params min_x_field: a min x field value.
    :params max_x_field: a max x field value.
    :params period_x_field: a period x field value.
    :return: A list of objects.
    """
    try:
        data = await api_service.dashboard_widget(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            min_x_field=min_x_field,
            max_x_field=max_x_field,
            period_x_field=period_x_field,
        )
        return data
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.get("/list/{model}")
async def list_objs(
    request: Request,
    model: str,
    search: str | None = None,
    sort_by: str | None = None,
    offset: int | None = 0,
    limit: int | None = 10,
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
    try:
        objs, total = await api_service.list(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            search=search,
            sort_by=sort_by,
            filters=request.query_params._dict,
            offset=offset,
            limit=limit,
        )
        return {
            "total": total,
            "results": objs,
        }
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.get("/retrieve/{model}/{id}")
async def get(
    request: Request,
    model: str,
    id: UUID | int,
) -> Any:
    """This method is used to get an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An object.
    """
    try:
        return await api_service.get(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.post("/add/{model}")
async def add(
    request: Request,
    model: str,
    payload: dict,
) -> Any:
    """This method is used to add an object.

    :params model: a name of model.
    :params payload: a payload object.
    :return: An object.
    """
    try:
        return await api_service.add(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            payload,
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.patch("/change-password/{id}")
async def change_password(
    request: Request,
    id: UUID | int,
    payload: dict,
) -> UUID | int:
    """This method is used to change password.

    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    try:
        await api_service.change_password(request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None), id, payload)
        return id
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.patch("/change/{model}/{id}")
async def change(
    request: Request,
    model: str,
    id: UUID | int,
    payload: dict,
) -> Any:
    """This method is used to change an object.

    :params model: a name of model.
    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    try:
        return await api_service.change(request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None), model, id, payload)
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.post("/export/{model}")
async def export(
    request: Request,
    model: str,
    payload: ExportInputSchema,
    search: str | None = None,
    sort_by: str | None = None,
):
    """This method is used to export a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params payload: a payload object.
    :params search: a search string.
    :params sort_by: a sort by string.
    :return: A stream of export data.
    """
    try:
        file_name, content_type, stream = await api_service.export(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            payload,
            search=search,
            sort_by=sort_by,
            filters=request.query_params._dict,
        )
        headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}
        return StreamingResponse(
            stream,  # type: ignore [arg-type]
            headers=headers,
            media_type=content_type,
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.delete("/delete/{model}/{id}")
async def delete(
    request: Request,
    model: str,
    id: UUID | int,
) -> UUID | int:
    """This method is used to delete an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An id of object.
    """
    try:
        return await api_service.delete(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.post("/action/{model}/{action}")
async def action(
    request: Request,
    model: str,
    action: str,
    payload: ActionInputSchema,
) -> None:
    """This method is used to perform an action.

    :params model: a name of model.
    :params action: a name of action.
    :params payload: a payload object.
    :return: A list of objects.
    """
    try:
        return await api_service.action(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            action,
            payload,
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.get("/configuration")
async def configuration(
    request: Request,
) -> ConfigurationSchema:
    """This method is used to get a configuration.

    :params user_id: an id of user.
    :return: A configuration.
    """
    return await api_service.get_configuration(
        request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
    )
