import logging

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from backend.depends import get_session_id, validate_session_id
from backend.schemas.api import SignInInputSchema
from backend.schemas.configuration import ConfigurationSchema, ModelSchema
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
            ModelSchema(name="test", fields=[]),
            ModelSchema(name="test1", fields=[]),
        ],
    )
