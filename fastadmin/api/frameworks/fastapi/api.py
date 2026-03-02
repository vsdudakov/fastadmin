import logging
from dataclasses import asdict
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.datastructures import UploadFile
from fastapi.responses import Response, StreamingResponse

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.helpers import parse_list_filters_from_query_params
from fastadmin.api.schemas import (
    ExportInputSchema,
    SignInInputSchema,
)
from fastadmin.api.service import ApiService, get_user_id_from_session_id
from fastadmin.models.schemas import (
    ActionInputSchema,
    ActionResponseSchema,
    ActionResponseType,
    ConfigurationSchema,
    WidgetActionInputSchema,
)
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
            request=request,
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
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            settings.ADMIN_USER_MODEL,
            user_id,
            request=request,
        )
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
        list_filters = parse_list_filters_from_query_params(
            request.query_params.keys,
            request.query_params.getlist,
            exclude={"search", "sort_by", "offset", "limit"},
        )
        objs, total = await api_service.list(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            search=search,
            sort_by=sort_by,
            filters=list_filters,
            offset=offset,
            limit=limit,
            request=request,
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
    id: UUID | int | str,
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
            request=request,
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
            request=request,
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.patch("/change-password/{id}")
async def change_password(
    request: Request,
    id: UUID | int | str,
    payload: dict,
) -> UUID | int | str:
    """This method is used to change password.

    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    try:
        await api_service.change_password(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            id,
            payload,
            request=request,
        )
        return id
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.patch("/change/{model}/{id}")
async def change(
    request: Request,
    model: str,
    id: UUID | int | str,
    payload: dict,
) -> Any:
    """This method is used to change an object.

    :params model: a name of model.
    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    try:
        return await api_service.change(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
            payload,
            request=request,
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.post("/upload-file/{model}/{field_name}")
async def upload_file(
    request: Request,
    model: str,
    field_name: str,
    file: UploadFile,
) -> str:
    """This method is used to upload files.

    :params request: a request object.
    :params model: a name of model.
    :params field_name: a name of field.
    :params file: a file object.
    :return: A file url.
    """
    try:
        file_name = file.filename
        if not file_name:
            raise HTTPException(422, detail="File name not found")
        file_content = await file.read()
        return await api_service.upload_file(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            field_name,
            file_name,
            file_content,
            request=request,
        )
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
        list_filters = parse_list_filters_from_query_params(
            request.query_params.keys,
            request.query_params.getlist,
            exclude={"search", "sort_by", "offset", "limit"},
        )
        file_name, content_type, stream = await api_service.export(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            payload,
            search=search,
            sort_by=sort_by,
            filters=list_filters,
            request=request,
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
    id: UUID | int | str,
) -> UUID | int | str:
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
            request=request,
        )
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.post("/action/{model}/{action}")
async def action(
    request: Request,
    model: str,
    action: str,
    payload: ActionInputSchema,
) -> dict:
    """This method is used to perform an action.

    :params model: a name of model.
    :params action: a name of action.
    :params payload: a payload object.
    :return: action result.
    """
    try:
        response = await api_service.action(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            action,
            payload,
            request=request,
        )
        if not response:
            response = ActionResponseSchema(
                type=ActionResponseType.MESSAGE,
                data="Successfully applied",
            )
        return asdict(response)
    except AdminApiException as e:
        raise HTTPException(e.status_code, detail=e.detail) from None


@router.post("/widget-action/{model}/{widget_action}")
async def widget_action(
    request: Request,
    model: str,
    widget_action: str,
    payload: WidgetActionInputSchema,
) -> dict:
    """This method is used to perform an action.

    :params model: a name of model.
    :params widget_action: a name of action.
    :params payload: a payload object.
    :return: action result.
    """
    try:
        response = await api_service.widget_action(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            widget_action,
            payload,
            request=request,
        )
        return asdict(response)
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
        request=request,
    )
