import json
import logging
from dataclasses import asdict
from datetime import datetime, time
from functools import wraps
from uuid import UUID

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.http import JsonResponse as BaseJsonResponse
from django.http import StreamingHttpResponse
from django.http.request import HttpRequest

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.helpers import is_valid_id
from fastadmin.api.schemas import ActionInputSchema, ExportInputSchema, SignInInputSchema
from fastadmin.api.service import ApiService, get_user_id_from_session_id
from fastadmin.settings import settings

logger = logging.getLogger(__name__)
api_service = ApiService()


class JsonEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime | time):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, ImageFieldFile | FieldFile):
            try:
                return o.url
            except ValueError:
                return None
        return super().default(o)


class JsonResponse(BaseJsonResponse):
    def __init__(self, *args, **kwargs):
        kwargs["encoder"] = JsonEncoder
        super().__init__(*args, **kwargs)


def csrf_exempt(view_func):
    async def wrapped_view(*args, **kwargs):
        return await view_func(*args, **kwargs)

    wrapped_view.csrf_exempt = True
    return wraps(view_func)(wrapped_view)


@csrf_exempt
async def sign_in(request: HttpRequest) -> JsonResponse:
    """This method is used to sign in.

    :params response: a response object.
    :params payload: a payload object.
    :return: None.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    try:
        payload = SignInInputSchema(**json.loads(request.body))
        session_id = await api_service.sign_in(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            payload,
        )

        response = JsonResponse({})
        response.set_cookie(settings.ADMIN_SESSION_ID_KEY, value=session_id, httponly=True)
        return response

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def sign_out(request: HttpRequest) -> JsonResponse:
    """This method is used to sign out.

    :params response: a response object.
    :return: None.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    try:
        response = JsonResponse({})
        if await api_service.sign_out(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
        ):
            response.delete_cookie(settings.ADMIN_SESSION_ID_KEY)
        return response

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def me(request: HttpRequest) -> JsonResponse:
    """This method is used to get current user.

    :params user_id: a user id.
    :return: A user object.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        user_id = await get_user_id_from_session_id(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
        )
        if not user_id:
            raise AdminApiException(401, "User is not authenticated.")
        obj = await api_service.get(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None), settings.ADMIN_USER_MODEL, user_id
        )
        return JsonResponse(obj)

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def dashboard_widget(request: HttpRequest, model: str) -> JsonResponse:
    """This method is used to get a dashboard widget data.

    :params model: a dashboard widget model.
    :params min_x_field: a min x field value.
    :params max_x_field: a max x field value.
    :params period_x_field: a period x field value.
    :return: A list of objects.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    filters = request.GET.dict()
    min_x_field = filters.get("min_x_field", None)
    max_x_field = filters.get("max_x_field", None)
    period_x_field = filters.get("period_x_field", None)

    try:
        data = await api_service.dashboard_widget(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            min_x_field=min_x_field,
            max_x_field=max_x_field,
            period_x_field=period_x_field,
        )
        return JsonResponse(data)
    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def list_objs(request: HttpRequest, model: str) -> JsonResponse:
    """This method is used to get a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params search: a search string.
    :params sort_by: a sort by string.
    :params offset: an offset.
    :params limit: a limit.
    :return: A list of objects.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        filters = request.GET.dict()
        search = filters.get("search", None)
        sort_by = filters.get("sort_by", None)
        offset = int(filters.get("offset", 0))
        limit = int(filters.get("limit", 10))

        objs, total = await api_service.list(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            search=search,
            sort_by=sort_by,
            filters=filters,
            offset=offset,
            limit=limit,
        )
        return JsonResponse(
            {
                "total": total,
                "results": objs,
            }
        )
    except ValueError:
        return JsonResponse({"detail": "Invalid format of get parameters"}, status=422)
    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def get(request: HttpRequest, model: str, id: UUID | int) -> JsonResponse:
    """This method is used to get an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An object.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    if not is_valid_id(id):
        return JsonResponse({"error": "Invalid id. It must be a UUID or an integer."}, status=422)
    try:
        obj = await api_service.get(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
        )
        return JsonResponse(obj)

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def add(request: HttpRequest, model: str) -> JsonResponse:
    """This method is used to add an object.

    :params model: a name of model.
    :params payload: a payload object.
    :return: An object.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        obj = await api_service.add(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            json.loads(request.body),
        )
        return JsonResponse(obj)
    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def change_password(request: HttpRequest, id: UUID | int) -> JsonResponse:
    """This method is used to change a password.

    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    if not is_valid_id(id):
        return JsonResponse({"error": "Invalid id. It must be a UUID or an integer."}, status=422)
    try:
        await api_service.change_password(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            id,
            json.loads(request.body),
        )
        return JsonResponse(id, safe=False)

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def change(request: HttpRequest, model: str, id: UUID | int) -> JsonResponse:
    """This method is used to change an object.

    :params model: a name of model.
    :params id: an id of object.
    :params payload: a payload object.
    :return: An object.
    """
    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    if not is_valid_id(id):
        return JsonResponse({"error": "Invalid id. It must be a UUID or an integer."}, status=422)
    try:
        obj = await api_service.change(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
            json.loads(request.body),
        )
        return JsonResponse(obj)

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def export(request: HttpRequest, model: str) -> JsonResponse:
    """This method is used to export a list of objects.

    :params request: a request object.
    :params model: a name of model.
    :params payload: a payload object.
    :params search: a search string.
    :params sort_by: a sort by string.
    :return: A stream of export data.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    filters = request.GET.dict()
    search = filters.get("search", None)
    sort_by = filters.get("sort_by", None)
    try:
        payload = ExportInputSchema(**json.loads(request.body))
        file_name, content_type, stream = await api_service.export(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            payload,
            search=search,
            sort_by=sort_by,
            filters=filters,
        )
        response = StreamingHttpResponse(stream, content_type=content_type)
        response.headers["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def delete(
    request: HttpRequest,
    model: str,
    id: UUID | int,
) -> JsonResponse:
    """This method is used to delete an object.

    :params model: a name of model.
    :params id: an id of object.
    :return: An id of object.
    """
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    if not is_valid_id(id):
        return JsonResponse({"error": "Invalid id. It must be a UUID or an integer."}, status=422)
    try:
        deleted_id = await api_service.delete(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            id,
        )
        return JsonResponse(deleted_id, safe=False)

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def action(
    request: HttpRequest,
    model: str,
    action: str,
) -> JsonResponse:
    """This method is used to perform an action.

    :params model: a name of model.
    :params action: a name of action.
    :params payload: a payload object.
    :return: A list of objects.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        payload = ActionInputSchema(**json.loads(request.body))
        await api_service.action(
            request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
            model,
            action,
            payload,
        )
        return JsonResponse({})

    except AdminApiException as e:
        return JsonResponse({"detail": e.detail}, status=e.status_code)


@csrf_exempt
async def configuration(request: HttpRequest) -> JsonResponse:
    """This method is used to get a configuration.

    :params user_id: an id of user.
    :return: A configuration.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    obj = await api_service.get_configuration(
        request.COOKIES.get(settings.ADMIN_SESSION_ID_KEY, None),
    )
    return JsonResponse(asdict(obj))
