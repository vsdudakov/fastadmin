from datetime import datetime, timedelta

import jwt
from fastapi import Request

from fastadmin import register_admin_model_class, unregister_admin_model_class
from fastadmin.api.frameworks.fastapi.depends import get_user_id_or_none
from fastadmin.settings import settings
from tests.models.orms.tortoise.admins import UserModelAdmin


async def test_get_user_id_or_none(tortoise_superuser):
    register_admin_model_class(UserModelAdmin, [tortoise_superuser.__class__])

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

    unregister_admin_model_class([tortoise_superuser.__class__])
