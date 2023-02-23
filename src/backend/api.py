import logging
from io import StringIO
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, StreamingResponse

from backend.depends import get_session_id, validate_session_id
from backend.schemas.api import ExportSchema, SignInInputSchema
from backend.schemas.configuration import (
    ChangeConfigurationFieldSchema,
    ConfigurationSchema,
    ListConfigurationFieldSchema,
    ModelFieldSchema,
    ModelPermission,
    ModelSchema,
    WidgetType,
)
from settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.post("/sign-in")
async def sign_in(
    payload: SignInInputSchema,
    response: Response,
):
    logger.info(payload)
    response.set_cookie(settings.ADMIN_SESSION_ID_KEY, value="test", httponly=True)
    return None


@router.post("/sign-out")
async def sign_out(
    response: Response,
    _: str = Depends(validate_session_id),
):
    response.delete_cookie(settings.ADMIN_SESSION_ID_KEY)
    return None


@router.get("/me")
async def me(
    session_id: str = Depends(validate_session_id),
):
    return {
        "username": "testdd",
        "id": "id",
    }


@router.get("/list/{model}")
async def list(
    request: Request,
    response: Response,
    model: str,
    sort_by: str = "-created_at",
    offset: int | None = 0,
    limit: int | None = 10,
    _: str = Depends(validate_session_id),
):
    filters = {k: v for k, v in request.query_params._dict.items() if k not in ["sort_by", "offset", "limit"]}
    logger.info("List %s", model)
    objs = [{"id": 1, "username": "test"}]
    return {
        "total": 10,
        "results": objs,
    }


@router.get("/retrieve/{model}/{id}")
async def get(
    request: Request,
    response: Response,
    model: str,
    id: str,
    _: str = Depends(validate_session_id),
):
    logger.info("Get %s: %s", model, id)
    return {"id": 1, "username": "test"}


@router.post("/add/{model}")
async def add(
    request: Request,
    response: Response,
    model: str,
    payload: dict,
    _: str = Depends(validate_session_id),
):
    logger.info("Add %s", model)
    return None


@router.patch("/change/{model}/{id}")
async def change(
    request: Request,
    response: Response,
    model: str,
    id: str,
    payload: dict,
    _: str = Depends(validate_session_id),
):
    logger.info("Get %s: %s", model, id)
    return None


@router.post("/export/{model}")
async def export(
    request: Request,
    response: Response,
    model: str,
    payload: ExportSchema,
    _: str = Depends(validate_session_id),
):
    logger.info("Export %s", model)
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
    _: str = Depends(validate_session_id),
):
    logger.info("Delete %s: %s", model, id)
    return None


@router.get("/configuration")
async def configuration(
    session_id: str | None = Depends(get_session_id),
):
    if not session_id:
        return ConfigurationSchema(
            site_name=settings.ADMIN_SITE_NAME,
            site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
            site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
            site_favicon=settings.ADMIN_SITE_FAVICON,
            primary_color=settings.ADMIN_PRIMARY_COLOR,
            models=[],
        )

    return ConfigurationSchema(
        site_name=settings.ADMIN_SITE_NAME,
        site_sign_in_logo=settings.ADMIN_SITE_SIGN_IN_LOGO,
        site_header_logo=settings.ADMIN_SITE_HEADER_LOGO,
        site_favicon=settings.ADMIN_SITE_FAVICON,
        primary_color=settings.ADMIN_PRIMARY_COLOR,
        models=[
            ModelSchema(
                name="User",
                permissions=[
                    ModelPermission.Add,
                    ModelPermission.Change,
                    ModelPermission.Delete,
                    ModelPermission.Export,
                ],
                fields=[
                    ModelFieldSchema(
                        name="username",
                        list_configuration=ListConfigurationFieldSchema(
                            sorter=True,
                            widget_type=WidgetType.RangePicker,
                        ),
                        change_configuration=ChangeConfigurationFieldSchema(
                            widget_type=WidgetType.Input,
                        ),
                    )
                ],
            ),
        ],
    )
