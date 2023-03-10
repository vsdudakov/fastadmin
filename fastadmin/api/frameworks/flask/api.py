import logging
from uuid import UUID

from flask import Blueprint, Response, make_response, request
from werkzeug.exceptions import HTTPException

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.helpers import get_user_id_from_session_id, is_valid_id
from fastadmin.api.schemas import ActionInputSchema, ExportInputSchema, SignInInputSchema
from fastadmin.api.service import ApiService
from fastadmin.models.exceptions import AdminModelException
from fastadmin.models.schemas import ConfigurationSchema
from fastadmin.settings import settings

logger = logging.getLogger(__name__)
api_router = Blueprint("api_router", __name__, url_prefix="/api")
api_service = ApiService()


@api_router.route("/sign-in", methods=["POST"])
async def sign_in():
    """This method is used to sign in.

    :params response: a response object.
    :params payload: a payload object.
    :return: None.
    """
    try:
        payload = SignInInputSchema(**request.json)
        session_id = await api_service.sign_in(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            payload,
        )
        response = make_response({})
        response.set_cookie(settings.ADMIN_SESSION_ID_KEY, value=session_id, httponly=True)
        return response
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/sign-out", methods=["POST"])
async def sign_out():
    """This method is used to sign out.

    :params response: a response object.
    :return: None.
    """
    try:
        if await api_service.sign_out(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
        ):
            response = make_response({})
            response.delete_cookie(settings.ADMIN_SESSION_ID_KEY)
            return response
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


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
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None), settings.ADMIN_USER_MODEL, user_id
        )
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/list/<string:model>", methods=["GET"])
async def list(model: str):
    """This method is used to get a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params search: a search string.
    :params sort_by: a sort by string.
    :params offset: an offset.
    :params limit: a limit.
    :return: A list of objects.
    """
    filters = request.args.to_dict()
    search = filters.get("search", None)
    sort_by = filters.get("sort_by", None)
    offset = int(filters.get("offset", 0))
    limit = int(filters.get("limit", 10))
    try:
        objs, total = await api_service.list(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            search=search,
            sort_by=sort_by,
            filters=filters,
            offset=offset,
            limit=limit,
        )
        return {
            "total": total,
            "results": objs,
        }
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/retrieve/<string:model>/<string:id>", methods=["GET"])
async def get(model: str, id: UUID | int) -> dict:
    """This method is used to get an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An object.
    """
    if not is_valid_id(id):
        http_exception = HTTPException("Invalid id. It must be a UUID or an integer.")
        http_exception.code = 422
        raise http_exception
    try:
        return await api_service.get(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
        )
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/add/<string:model>", methods=["POST"])
async def add(model: str) -> dict:
    """This method is used to add an object.

    :params model: a name of model.
    :params payload: a payload object.
    :return: An object.
    """
    try:
        return await api_service.add(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            request.json,
        )
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/change/<string:model>/<string:id>", methods=["PATCH"])
async def change(model: str, id: UUID | int) -> dict:
    """This method is used to change an object.

    :params model: a name of model.
    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    if not is_valid_id(id):
        http_exception = HTTPException("Invalid id. It must be a UUID or an integer.")
        http_exception.code = 422
        raise http_exception
    try:
        return await api_service.change(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None), model, id, request.json
        )
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/export/<string:model>", methods=["POST"])
async def export(model: str):
    """This method is used to export a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params payload: a payload object.
    :params search: a search string.
    :params sort_by: a sort by string.
    :return: A stream of export data.
    """
    filters = request.args.to_dict()
    search = filters.get("search", None)
    sort_by = filters.get("sort_by", None)
    try:
        payload = ExportInputSchema(**request.json)
        file_name, stream = await api_service.export(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            payload,
            search=search,
            sort_by=sort_by,
            filters=request.query_params._dict,
        )
        response = Response(stream, mimetype="text/csv")
        response.headers["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/delete/<string:model>/<string:id>", methods=["DELETE"])
async def delete(
    model: str,
    id: UUID | int,
) -> UUID | int:
    """This method is used to delete an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An id of object.
    """
    if not is_valid_id(id):
        http_exception = HTTPException("Invalid id. It must be a UUID or an integer.")
        http_exception.code = 422
        raise http_exception
    try:
        return await api_service.delete(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
        )
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/change/<string:model>/<string:action>", methods=["POST"])
async def action(
    model: str,
    action: str,
) -> None:
    """This method is used to perform an action.

    :params model: a name of model.
    :params action: a name of action.
    :params payload: a payload object.
    :return: A list of objects.
    """
    try:
        payload = ActionInputSchema(**request.json)
        return await api_service.action(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            action,
            payload,
        )
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception


@api_router.route("/configuration", methods=["GET"])
async def configuration():
    """This method is used to get a configuration.

    :params user_id: an id of user.
    :return: A configuration.
    """
    try:
        obj = await api_service.get_configuration(
            request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None),
        )
        return obj.dict()
    except AdminModelException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = 422
        raise http_exception
    except AdminApiException as e:
        http_exception = HTTPException(e.detail)
        http_exception.code = e.status_code
        raise http_exception
