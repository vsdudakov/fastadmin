from datetime import datetime
from uuid import UUID

import jwt

from fastadmin.models.helpers import get_admin_model
from fastadmin.settings import settings


def sanitize(value: str) -> bool | None | str:
    """Sanitize value

    :params value: a value.
    :return: A sanitized value.
    """
    if value == "false":
        return False
    elif value == "true":
        return True
    elif value == "null":
        return None
    return value


def is_valid_uuid(uuid_to_test: str) -> bool:
    """Check if uuid_to_test is a valid uuid.

    :param uuid_to_test: A uuid to test.
    :return: True if uuid_to_test is a valid uuid, False otherwise.
    """
    try:
        uuid_obj = UUID(uuid_to_test)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def is_digit(digit_to_test: str) -> bool:
    """Check if digit_to_test is a digit.

    :param digit_to_test: A digit to test.
    :return: True if digit_to_test is a digit, False otherwise.
    """
    try:
        int(digit_to_test)
    except ValueError:
        return False
    return True


def is_valid_id(id: UUID | int) -> bool:
    """Check if id is a valid id.

    :param id: An id to test.
    :return: True if id is a valid id, False otherwise.
    """
    return is_digit(str(id)) or is_valid_uuid(str(id))


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

    if datetime.fromisoformat(session_expired_at) < datetime.utcnow():
        return None

    user_id = token_payload.get("user_id")

    if not user_id or not await admin_model.get_obj(user_id):
        return None

    return user_id
