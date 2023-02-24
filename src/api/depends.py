from fastapi import Request, status
from fastapi.exceptions import HTTPException

from models import get_admin_model
from settings import settings


async def get_session_id(request: Request) -> str | None:
    return request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None)


async def get_user_id(request: Request) -> str:
    session_id = await get_session_id(request)
    if not session_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    admin_model = get_admin_model(settings.ADMIN_USER_MODEL)
    if not admin_model:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Admin model for user is not registered.")
    id = session_id
    if not await admin_model.get_obj(request, id):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return id
