from datetime import datetime

import jwt
from fastapi import Request, status
from fastapi.exceptions import HTTPException

from fastadmin.models.helpers import get_admin_model
from fastadmin.settings import settings


async def get_user_id_or_none(request: Request) -> str | None:
    """This method is used to get user id from request or None.

    :params request: a request object.
    :return: A user id or None.
    """
    admin_model = get_admin_model(settings.ADMIN_USER_MODEL)
    if not admin_model:
        return None

    session_id = request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None)
    if not session_id:
        return None

    try:
        token_payload = jwt.decode(session_id, settings.ADMIN_SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

    session_expired_at = token_payload.get("session_expired_at")
    if not session_expired_at:
        return None

    if datetime.fromisoformat(session_expired_at) < datetime.utcnow():
        return None

    user_id = token_payload.get("user_id")

    if not user_id or not await admin_model.get_obj(user_id):
        return None

    return user_id


async def get_user_id(request: Request) -> str:
    """This method is used to get user id from request.

    :params request: a request object.
    :return: A user id.
    """
    user_id = await get_user_id_or_none(request)
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return user_id
