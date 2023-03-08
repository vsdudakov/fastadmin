from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.models.orms.tortoise.admins import UserModelAdmin


async def sign_in(fastapi_client, tortoise_user):
    register_admin_model_class(UserModelAdmin, [tortoise_user.__class__])
    r = await fastapi_client.post(
        "/api/sign-in",
        json={
            "username": tortoise_user.username,
            "password": tortoise_user.password,
        },
    )
    assert r.status_code == 200
    assert r.json() is None
    return r.cookies


async def sign_out(fastapi_client, tortoise_user):
    r = await fastapi_client.post("/api/sign-out")
    assert r.status_code == 200
    assert r.json() is None
    unregister_admin_model_class([tortoise_user.__class__])
