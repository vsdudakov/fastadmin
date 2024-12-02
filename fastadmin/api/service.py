import inspect
import logging
import re
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from io import BytesIO, StringIO
from typing import Any, cast
from uuid import UUID

import jwt
from asgiref.sync import sync_to_async

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.helpers import sanitize_filter_key, sanitize_filter_value
from fastadmin.api.schemas import (
    ActionInputSchema,
    ChangePasswordInputSchema,
    DashboardWidgetDataOutputSchema,
    DashboardWidgetQuerySchema,
    ExportFormat,
    ExportInputSchema,
    ListQuerySchema,
    SignInInputSchema,
)
from fastadmin.models.base import InlineModelAdmin, ModelAdmin, admin_dashboard_widgets
from fastadmin.models.helpers import (
    generate_dashboard_widgets_schema,
    generate_models_schema,
    get_admin_model,
    get_admin_models,
    get_admin_or_admin_inline_model,
)
from fastadmin.models.schemas import ConfigurationSchema, ModelSchema
from fastadmin.settings import settings

logger = logging.getLogger(__name__)


def convert_id(id: str | int | UUID) -> int | UUID | None:
    """Convert the given id to int or UUID.

    :param id: A string value.
    :return: An int or UUID value. Or None if the given id is invalid.
    """
    if isinstance(id, int | UUID):
        return id

    # Check if the input_str is an integer
    if re.fullmatch(r"\d+", id):
        return int(id)

    # Check if the input_str is a valid UUID
    if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", id):
        return UUID(id)

    logger.warning("Invalid id: %s", id)
    return None


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

    if datetime.fromisoformat(session_expired_at).replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return None

    user_id = token_payload.get("user_id")
    if not user_id:
        return None

    user_id = convert_id(user_id)
    if not user_id or not await admin_model.get_obj(user_id):
        return None

    return user_id


class ApiService:
    async def sign_in(
        self,
        session_id: str | None,
        payload: SignInInputSchema,
    ) -> str:
        model = settings.ADMIN_USER_MODEL
        admin_model = get_admin_model(model)

        if not admin_model:
            raise AdminApiException(401, detail=f"{model} model is not registered.")

        if inspect.iscoroutinefunction(admin_model.authenticate):
            authenticate_fn = admin_model.authenticate
        else:
            authenticate_fn = sync_to_async(admin_model.authenticate)  # type: ignore [arg-type]

        user_id = await authenticate_fn(payload.username, payload.password)

        if not user_id or not isinstance(user_id, int | UUID):
            raise AdminApiException(401, detail="Invalid credentials.")

        now = datetime.now(timezone.utc)
        session_expired_at = now + timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
        if isinstance(user_id, UUID):
            user_id = str(user_id)
        return jwt.encode(
            {
                "user_id": user_id,
                "session_expired_at": session_expired_at.isoformat(),
            },
            settings.ADMIN_SECRET_KEY,
            algorithm="HS256",
        )

    async def sign_out(
        self,
        session_id: str | None,
    ) -> bool:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        return True

    async def dashboard_widget(
        self,
        session_id: str | None,
        model: str,
        min_x_field: str | None = None,
        max_x_field: str | None = None,
        period_x_field: str | None = None,
    ) -> dict[str, str | int | float]:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        query_params = DashboardWidgetQuerySchema(
            min_x_field=min_x_field,
            max_x_field=max_x_field,
            period_x_field=period_x_field,
        )

        dashboard_widget_model = admin_dashboard_widgets.get(model)
        if not dashboard_widget_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        if inspect.iscoroutinefunction(dashboard_widget_model.get_data):
            get_data = dashboard_widget_model.get_data
        else:
            get_data = sync_to_async(dashboard_widget_model.get_data)  # type: ignore [arg-type]
        data = await get_data(
            min_x_field=query_params.min_x_field,
            max_x_field=query_params.max_x_field,
            period_x_field=query_params.period_x_field,
        )

        DashboardWidgetDataOutputSchema(**data)
        return data

    async def list(
        self,
        session_id: str | None,
        model: str,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
        offset: int | None = 0,
        limit: int | None = 10,
    ) -> tuple[list[dict], int]:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        query_params = ListQuerySchema(
            search=search,
            sort_by=sort_by,
            filters=filters or {},
            offset=offset,
            limit=limit,
        )

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        # validations
        fields = admin_model.get_fields_for_serialize()

        if query_params.search and admin_model.search_fields:
            for field in admin_model.search_fields:
                if field not in fields:
                    raise AdminApiException(422, detail=f"Search by {field} is not allowed")

        exclude_filter_fields = ("search", "sort_by", "offset", "limit")
        query_filters: dict[tuple[str, str], bool | str | None] | None = None
        if query_params.filters:
            for k in query_params.filters:
                if k in exclude_filter_fields:
                    continue
                field = k.split("__", 1)[0]
                if field not in fields:
                    raise AdminApiException(422, detail=f"Filter by {k} is not allowed")
            query_filters = {
                sanitize_filter_key(k, admin_model.get_model_fields_with_widget_types()): sanitize_filter_value(v)
                for k, v in query_params.filters.items()
                if k not in exclude_filter_fields
            }

        if query_params.sort_by:
            if query_params.sort_by.strip("-") not in fields:
                raise AdminApiException(422, detail=f"Sort by {query_params.sort_by} is not allowed")
        elif admin_model.ordering:
            for ordering_field in admin_model.ordering:
                if ordering_field.strip("-") not in fields:
                    raise AdminApiException(422, detail=f"Sort by {ordering_field} is not allowed")

        if admin_model.list_select_related:
            for field in admin_model.list_select_related:
                if field not in fields:
                    raise AdminApiException(422, detail=f"Select related by {field} is not allowed")

        return await admin_model.get_list(
            offset=query_params.offset,
            limit=query_params.limit,
            search=query_params.search,
            sort_by=query_params.sort_by,
            filters=query_filters,
        )

    async def get(
        self,
        session_id: str | None,
        model: str,
        id: UUID | int,
    ) -> dict:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        obj = await admin_model.get_obj(id)
        if not obj:
            raise AdminApiException(404, detail=f"{model} not found.")
        return obj

    async def add(
        self,
        session_id: str | None,
        model: str,
        payload: dict,
    ) -> dict:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")
        return await admin_model.save_model(None, payload)  # type: ignore [return-value]

    async def change_password(
        self,
        session_id: str | None,
        id: UUID | int,
        payload: dict,
    ) -> None:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        admin_model = get_admin_model(settings.ADMIN_USER_MODEL)
        if not admin_model:
            raise AdminApiException(404, detail=f"{settings.ADMIN_USER_MODEL} model is not registered.")

        payload = ChangePasswordInputSchema(**payload)
        if payload.password != payload.confirm_password:
            raise AdminApiException(422, detail="Passwords do not match")

        if not hasattr(admin_model, "change_password"):
            raise AdminApiException(
                404, detail=f"{settings.ADMIN_USER_MODEL} admin class has no change_password method."
            )

        if inspect.iscoroutinefunction(admin_model.change_password):
            change_password_fn = admin_model.change_password
        else:
            change_password_fn = sync_to_async(admin_model.change_password)  # type: ignore [arg-type]
        await change_password_fn(id, payload.password)

    async def change(
        self,
        session_id: str | None,
        model: str,
        id: UUID | int,
        payload: dict,
    ) -> dict:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        obj = await admin_model.save_model(id, payload)
        if not obj:
            raise AdminApiException(404, detail=f"{model} not found.")
        return obj

    async def export(
        self,
        session_id: str | None,
        model: str,
        payload: ExportInputSchema,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict | None = None,
    ) -> tuple[str, str, StringIO | BytesIO | None]:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        query_params = ListQuerySchema(
            search=search,
            sort_by=sort_by,
            filters=filters or {},
            offset=payload.offset,
            limit=payload.limit,
        )

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        # validations
        fields = admin_model.get_fields_for_serialize()

        if query_params.search and admin_model.search_fields:
            for field in admin_model.search_fields:
                if field not in fields:
                    raise AdminApiException(422, detail=f"Search by {field} is not allowed")

        exclude_filter_fields = ("search", "sort_by", "offset", "limit")
        query_filters: dict[tuple[str, str], bool | str | None] | None = None
        if query_params.filters:
            for k in query_params.filters:
                if k in exclude_filter_fields:
                    continue
                field = k.split("__", 1)[0]
                if field not in fields:
                    raise AdminApiException(422, detail=f"Filter by {k} is not allowed")
            query_filters = {
                sanitize_filter_key(k, admin_model.get_model_fields_with_widget_types()): sanitize_filter_value(v)
                for k, v in query_params.filters.items()
                if k not in exclude_filter_fields
            }

        if query_params.sort_by:
            if query_params.sort_by.strip("-") not in fields:
                raise AdminApiException(422, detail=f"Sort by {query_params.sort_by} is not allowed")
        elif admin_model.ordering:
            for ordering_field in admin_model.ordering:
                if ordering_field.strip("-") not in fields:
                    raise AdminApiException(422, detail=f"Sort by {ordering_field} is not allowed")

        content_type = "text/plain"
        file_name = f"{model}.txt"
        if payload.format == ExportFormat.CSV:
            content_type = "text/csv"
            file_name = f"{model}.csv"
        elif payload.format == ExportFormat.JSON:
            content_type = "text/plain"
            file_name = f"{model}.json"
        return (
            file_name,
            content_type,
            await admin_model.get_export(
                payload.format,
                offset=query_params.offset,
                limit=query_params.limit,
                search=query_params.search,
                sort_by=query_params.sort_by,
                filters=query_filters,
            ),
        )

    async def delete(
        self,
        session_id: str | None,
        model: str,
        id: UUID | int,
    ) -> UUID | int:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        if str(current_user_id) == str(id) and model == settings.ADMIN_USER_MODEL:
            raise AdminApiException(403, detail="You cannot delete yourself.")
        await admin_model.delete_model(id)
        return id

    async def action(self, session_id: str | None, model: str, action: str, payload: ActionInputSchema) -> None:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        if action not in admin_model.actions:
            raise AdminApiException(422, detail=f"{action} action is not in actions setting.")

        action_function = getattr(admin_model, action, None)
        if not action_function or not hasattr(action_function, "is_action"):
            raise AdminApiException(422, detail=f"{action} action is not registered.")

        if inspect.iscoroutinefunction(action_function):
            action_function_fn = action_function
        else:
            action_function_fn = sync_to_async(action_function)

        await action_function_fn(payload.ids)

    async def get_configuration(
        self,
        session_id: str | None,
    ) -> ConfigurationSchema:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            return ConfigurationSchema(
                site_name=settings.ADMIN_SITE_NAME,
                site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
                site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
                site_favicon=settings.ADMIN_SITE_FAVICON,
                primary_color=settings.ADMIN_PRIMARY_COLOR,
                username_field=settings.ADMIN_USER_MODEL_USERNAME_FIELD,
                date_format=settings.ADMIN_DATE_FORMAT,
                datetime_format=settings.ADMIN_DATETIME_FORMAT,
                disable_crop_image=settings.ADMIN_DISABLE_CROP_IMAGE,
                models=[],
                dashboard_widgets=[],
            )

        admin_models = cast(dict[Any, ModelAdmin | InlineModelAdmin], get_admin_models())
        models = cast(Sequence[ModelSchema], await generate_models_schema(admin_models, user_id=current_user_id))
        dashboard_widgets = generate_dashboard_widgets_schema()
        return ConfigurationSchema(
            site_name=settings.ADMIN_SITE_NAME,
            site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
            site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
            site_favicon=settings.ADMIN_SITE_FAVICON,
            primary_color=settings.ADMIN_PRIMARY_COLOR,
            username_field=settings.ADMIN_USER_MODEL_USERNAME_FIELD,
            date_format=settings.ADMIN_DATE_FORMAT,
            datetime_format=settings.ADMIN_DATETIME_FORMAT,
            disable_crop_image=settings.ADMIN_DISABLE_CROP_IMAGE,
            models=models,
            dashboard_widgets=dashboard_widgets,
        )  # type: ignore [call-arg]
