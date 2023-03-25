import inspect
from collections.abc import Sequence
from datetime import datetime, timedelta
from io import BytesIO, StringIO
from typing import Any, cast
from uuid import UUID

import jwt
from asgiref.sync import sync_to_async

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.helpers import get_user_id_from_session_id, sanitize
from fastadmin.api.schemas import ActionInputSchema, ExportInputSchema, SignInInputSchema
from fastadmin.models.base import InlineModelAdmin, ModelAdmin
from fastadmin.models.helpers import (
    generate_models_schema,
    get_admin_model,
    get_admin_models,
    get_admin_or_admin_inline_model,
)
from fastadmin.models.schemas import ConfigurationSchema, ModelSchema
from fastadmin.settings import settings


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
            authenticate_fn = sync_to_async(admin_model.authenticate)

        user_id = await authenticate_fn(payload.username, payload.password)

        if not user_id or not (isinstance(user_id, int) or isinstance(user_id, UUID)):
            raise AdminApiException(401, detail="Invalid credentials.")

        now = datetime.utcnow()
        session_expired_at = now + timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
        return jwt.encode(
            {
                "user_id": str(user_id),
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

    async def list(
        self,
        session_id: str | None,
        model: str,
        search: str | None = None,
        sort_by: str | None = None,
        filters: dict = {},
        offset: int | None = 0,
        limit: int | None = 10,
    ) -> tuple[list[dict], int]:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        filters = {k: sanitize(v) for k, v in filters.items() if k not in ("search", "sort_by", "offset", "limit")}

        # validations
        fields = admin_model.get_fields_for_serialize()

        if search and admin_model.search_fields:
            for field in admin_model.search_fields:
                if field not in fields:
                    raise AdminApiException(422, detail=f"Search by {field} is not allowed")

        if filters:
            for filter_condition in filters.keys():
                field = filter_condition.split("__", 1)[0]
                if field not in fields:
                    raise AdminApiException(422, detail=f"Filter by {filter_condition} is not allowed")

        if sort_by:
            if sort_by.strip("-") not in fields:
                raise AdminApiException(422, detail=f"Sort by {sort_by} is not allowed")
        elif admin_model.ordering:
            for ordering_field in admin_model.ordering:
                if ordering_field.strip("-") not in fields:
                    raise AdminApiException(422, detail=f"Sort by {ordering_field} is not allowed")

        if admin_model.list_select_related:
            for field in admin_model.list_select_related:
                if field not in fields:
                    raise AdminApiException(422, detail=f"Select related by {field} is not allowed")

        return await admin_model.get_list(
            offset=offset,
            limit=limit,
            search=search,
            sort_by=sort_by,
            filters=filters,
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
        return await admin_model.save_model(None, payload)  # type: ignore

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
        filters: dict = {},
    ) -> tuple[str, StringIO | BytesIO | None]:
        current_user_id = await get_user_id_from_session_id(session_id)
        if not current_user_id:
            raise AdminApiException(401, detail="User is not authenticated.")

        admin_model = get_admin_or_admin_inline_model(model)
        if not admin_model:
            raise AdminApiException(404, detail=f"{model} model is not registered.")

        filters = {k: sanitize(v) for k, v in filters.items() if k not in ("search", "sort_by", "offset", "limit")}
        file_name = f"{model}.{(payload.format or 'csv').lower()}"
        return file_name, await admin_model.get_export(
            payload.format,
            search=search,
            sort_by=sort_by,
            filters=filters,
            offset=payload.offset,
            limit=payload.limit,
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
                models=[],
            )

        admin_models = cast(dict[Any, ModelAdmin | InlineModelAdmin], get_admin_models())
        models = cast(Sequence[ModelSchema], generate_models_schema(admin_models, user_id=current_user_id))
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
