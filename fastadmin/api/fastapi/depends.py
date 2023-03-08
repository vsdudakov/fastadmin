from uuid import UUID

from fastapi import Request, status
from fastapi.exceptions import HTTPException

from fastadmin.api.helpers import get_user_id_from_session_id
from fastadmin.settings import settings


async def get_user_id_or_none(request: Request) -> UUID | int | None:
    """This method is used to get user id from request or None.

    :params request: a request object.
    :return: A user id or None.
    """
    session_id = request.cookies.get(settings.ADMIN_SESSION_ID_KEY, None)
    if not session_id:
        return None

    return await get_user_id_from_session_id(session_id)


async def get_user_id(request: Request) -> UUID | int:
    """This method is used to get user id from request.

    :params request: a request object.
    :return: A user id.
    """
    user_id = await get_user_id_or_none(request)
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return user_id
