import logging
from dataclasses import asdict
from uuid import UUID

from flask import Blueprint, Response, make_response, request
from werkzeug.exceptions import HTTPException

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.helpers import is_valid_id, parse_list_filters_from_query_params
from fastadmin.api.schemas import (
    ExportInputSchema,
    SignInInputSchema,
)
from fastadmin.api.service import ApiService, get_user_id_from_session_id
from fastadmin.models.schemas import (
    ActionInputSchema,
    ActionResponseSchema,
    ActionResponseType,
    WidgetActionInputSchema,
)
from fastadmin.settings import settings

logger = logging.getLogger(__name__)
api_router = Blueprint("api_router", __name__, url_prefix="/api")
api_service = ApiService()


@api_router.route("/sign-in", methods=["POST"])
async def sign_in() -> Response:
    """This method is used to sign in.

    :params response: a response object.
    :params payload: a payload object.
    :return: None.
    """
    try:
        request_payload: dict = request.json
        payload = SignInInputSchema(**request_payload)
        session_id = await api_service.sign_in(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            payload,
            request=request,
        )
        response = make_response({})
        response.set_cookie(settings.ADMIN_SESSION_ID_KEY, value=session_id, httponly=True)
        return response
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/sign-out", methods=["POST"])
async def sign_out() -> Response:
    """This method is used to sign out.

    :params response: a response object.
    :return: None.
    """
    try:
        response = make_response({})
        if await api_service.sign_out(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
        ):
            response.delete_cookie(settings.ADMIN_SESSION_ID_KEY)
        return response
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/me", methods=["GET"])
async def me() -> dict:
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
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/list/<string:model>", methods=["GET"])
async def list_objs(model: str) -> dict:
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
        search = request.args.get("search") or None
        sort_by = request.args.get("sort_by") or None
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 10))
        list_filters = parse_list_filters_from_query_params(
            request.args.keys,
            request.args.getlist,
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
    except ValueError as e:
        http_exception = HTTPException("Invalid format of get parameters")
        http_exception.code = 422
        raise http_exception from e
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/retrieve/<string:model>/<string:id>", methods=["GET"])
async def get(model: str, id: UUID | int | str) -> dict:
    """This method is used to get an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An object.
    """
    if not is_valid_id(id):
        http_exception = HTTPException("Invalid id. It must be a UUID, an integer, or a non-empty string.")
        http_exception.code = 422
        raise http_exception
    try:
        return await api_service.get(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
            request=request,
        )
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/add/<string:model>", methods=["POST"])
async def add(model: str) -> dict:
    """This method is used to add an object.

    :params model: a name of model.
    :params payload: a payload object.
    :return: An object.
    """
    try:
        payload: dict = request.json
        return await api_service.add(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            payload,
            request=request,
        )
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/change-password/<string:id>", methods=["PATCH"])  # type: ignore [type-var]
async def change_password(id: UUID | int | str) -> UUID | int | str:
    """This method is used to change password.

    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    if not is_valid_id(id):
        http_exception = HTTPException("Invalid id. It must be a UUID, an integer, or a non-empty string.")
        http_exception.code = 422
        raise http_exception
    try:
        payload: dict = request.json
        await api_service.change_password(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            id,
            payload,
            request=request,
        )
        return id
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/change/<string:model>/<string:id>", methods=["PATCH"])
async def change(model: str, id: UUID | int | str) -> dict:
    """This method is used to change an object.

    :params model: a name of model.
    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    if not is_valid_id(id):
        http_exception = HTTPException("Invalid id. It must be a UUID, an integer, or a non-empty string.")
        http_exception.code = 422
        raise http_exception
    try:
        payload: dict = request.json
        return await api_service.change(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
            payload,
            request=request,
        )
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/upload-file/<string:model>/<string:field_name>", methods=["POST"])
async def upload_file(
    model: str,
    field_name: str,
) -> str:
    """This method is used to upload files.

    :params model: a name of model.
    :params field_name: a name of field.
    :return: A file url.
    """
    try:
        files = request.files.to_dict()
        file = files.get("file")
        if not file:
            http_exception = HTTPException("File not found")
            http_exception.code = 422
            raise http_exception from None
        file_name = file.filename
        if not file_name:
            http_exception = HTTPException("File name not found")
            http_exception.code = 422
            raise http_exception from None
        file_content = file.read()
        return await api_service.upload_file(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            field_name,
            file_name,
            file_content,
            request=request,
        )
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/export/<string:model>", methods=["POST"])
async def export(model: str) -> Response:
    """This method is used to export a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params payload: a payload object.
    :params search: a search string.
    :params sort_by: a sort by string.
    :return: A stream of export data.
    """
    search = request.args.get("search") or None
    sort_by = request.args.get("sort_by") or None
    list_filters = parse_list_filters_from_query_params(
        request.args.keys,
        request.args.getlist,
        exclude={"search", "sort_by", "offset", "limit"},
    )
    try:
        request_payload: dict = request.json
        payload: ExportInputSchema = ExportInputSchema(**request_payload)
        file_name, content_type, stream = await api_service.export(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            payload,
            search=search,
            sort_by=sort_by,
            filters=list_filters,
            request=request,
        )
        response = Response(stream, mimetype=content_type)
        response.headers["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/delete/<string:model>/<string:id>", methods=["DELETE"])  # type: ignore [type-var]
async def delete(
    model: str,
    id: UUID | int | str,
) -> UUID | int | str:
    """This method is used to delete an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An id of object.
    """
    if not is_valid_id(id):
        http_exception = HTTPException("Invalid id. It must be a UUID, an integer, or a non-empty string.")
        http_exception.code = 422
        raise http_exception
    try:
        return await api_service.delete(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
            request=request,
        )
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/action/<string:model>/<string:action>", methods=["POST"])
async def action(
    model: str,
    action: str,
) -> Response:
    """This method is used to perform an action.

    :params model: a name of model.
    :params action: a name of action.
    :params payload: a payload object.
    :return: action result.
    """
    try:
        request_payload: dict = request.json
        payload = ActionInputSchema(**request_payload)
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
        return make_response(asdict(response))
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/widget-action/<string:model>/<string:widget_action>", methods=["POST"])
async def widget_action(
    model: str,
    widget_action: str,
) -> Response:
    """This method is used to perform an action.

    :params model: a name of model.
    :params widget_action: a name of action.
    :params payload: a payload object.
    :return: action result.
    """
    try:
        request_payload: dict = request.json
        payload = WidgetActionInputSchema(**request_payload)
        response = await api_service.widget_action(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            widget_action,
            payload,
            request=request,
        )
        return make_response(asdict(response))
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception from e


@api_router.route("/configuration", methods=["GET"])
async def configuration() -> dict:
    """This method is used to get a configuration.

    :params user_id: an id of user.
    :return: A configuration.
    """
    obj = await api_service.get_configuration(
        request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
        request=request,
    )
    return asdict(obj)
