import uuid
from datetime import datetime, timedelta, timezone

import jwt

from fastadmin.api.helpers import is_valid_id, is_valid_uuid, sanitize_filter_value
from fastadmin.api.service import get_user_id_from_session_id
from fastadmin.settings import settings


async def test_sanitize_filter_value():
    assert sanitize_filter_value("true") is True
    assert sanitize_filter_value("false") is False
    assert sanitize_filter_value("null") is None
    assert sanitize_filter_value("foo") == "foo"


async def test_is_valid_uuid():
    assert is_valid_uuid(str(uuid.uuid1())) is True
    assert is_valid_uuid(str(uuid.uuid3(uuid.uuid4(), "test"))) is True
    assert is_valid_uuid(str(uuid.uuid4())) is True
    assert is_valid_uuid(str(uuid.uuid5(uuid.uuid4(), "test"))) is True
    assert is_valid_uuid("invalid") is False


async def test_is_valid_id():
    assert is_valid_id(1) is True
    assert is_valid_uuid(str(uuid.uuid1())) is True


async def test_get_user_id_from_session_id(session_id):
    assert await get_user_id_from_session_id(None) is None
    assert await get_user_id_from_session_id("invalid") is None
    user_id = await get_user_id_from_session_id(session_id)
    assert user_id is not None

    now = datetime.now(timezone.utc)
    session_expired_at = now + timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
    without_expired_session_id = jwt.encode(
        {
            "user_id": str(user_id),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    assert await get_user_id_from_session_id(without_expired_session_id) is None

    session_expired_at = now - timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
    expired_session_id = jwt.encode(
        {
            "user_id": str(user_id),
            "session_expired_at": session_expired_at.isoformat(),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    assert await get_user_id_from_session_id(expired_session_id) is None

    session_expired_at = now + timedelta(seconds=settings.ADMIN_SESSION_EXPIRED_AT)
    invalid_user_session_id = jwt.encode(
        {
            "user_id": str(-1),
            "session_expired_at": session_expired_at.isoformat(),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    assert await get_user_id_from_session_id(invalid_user_session_id) is None
