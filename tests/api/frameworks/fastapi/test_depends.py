from datetime import datetime, timedelta

import jwt
from fastapi import Request

from fastadmin.api.frameworks.fastapi.depends import get_user_id_or_none
from fastadmin.settings import settings


async def test_get_user_id_or_none(tortoise_superuser):
    request = Request(scope={"type": "http", "headers": []})
    assert await get_user_id_or_none(request) is None

    request.cookies[settings.ADMIN_SESSION_ID_KEY] = "invalid"
    assert await get_user_id_or_none(request) is None

    session_id = jwt.encode(
        {
            "user_id": str(tortoise_superuser.id),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    request.cookies[settings.ADMIN_SESSION_ID_KEY] = session_id
    assert await get_user_id_or_none(request) is None

    now = datetime.utcnow() - timedelta(seconds=10)
    session_id = jwt.encode(
        {
            "user_id": str(tortoise_superuser.id),
            "session_expired_at": now.isoformat(),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    request.cookies[settings.ADMIN_SESSION_ID_KEY] = session_id
    assert await get_user_id_or_none(request) is None

    now = datetime.utcnow() + timedelta(seconds=10)
    session_id = jwt.encode(
        {
            "user_id": -1,
            "session_expired_at": now.isoformat(),
        },
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    request.cookies[settings.ADMIN_SESSION_ID_KEY] = session_id
    assert await get_user_id_or_none(request) is None
