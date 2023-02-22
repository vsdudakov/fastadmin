from fastapi import Cookie, Request, status
from fastapi.exceptions import HTTPException

from settings import settings


async def get_session_id(request: Request) -> str | None:
    return request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None)


async def validate_session_id(request: Request) -> str:
    session_id = await get_session_id(request)
    if not session_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return session_id
