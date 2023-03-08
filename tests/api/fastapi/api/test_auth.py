from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.fastapi.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import UserModelAdmin


async def test_sign_in_401_invalid_password(tortoise_superuser, fastapi_client):
    register_admin_model_class(UserModelAdmin, [tortoise_superuser.__class__])
    r = await fastapi_client.post(
        "/api/sign-in",
        json={
            "username": tortoise_superuser.username,
            "password": "invalid",
        },
    )
    assert r.status_code == 401, r.text
    unregister_admin_model_class([tortoise_superuser.__class__])


async def test_sign_in_401(tortoise_superuser, fastapi_client):
    r = await fastapi_client.post(
        "/api/sign-in",
        json={
            "username": tortoise_superuser.username,
            "password": tortoise_superuser.password,
        },
    )
    assert r.status_code == 401, r.text


async def test_sign_in(tortoise_superuser, fastapi_client):
    assert await sign_in(fastapi_client, tortoise_superuser)
    await sign_out(fastapi_client, tortoise_superuser)


async def test_me(tortoise_superuser, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)

    r = await fastapi_client.get(
        "/api/me",
    )
    assert r.status_code == 200, r.text
    me = r.json()
    assert me["id"] == tortoise_superuser.id
    assert me["username"] == tortoise_superuser.username
    await sign_out(fastapi_client, tortoise_superuser)


async def test_me_401(fastapi_client):
    r = await fastapi_client.get("/api/me")
    assert r.status_code == 401, r.text


async def test_me_404(tortoise_superuser, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    unregister_admin_model_class([tortoise_superuser.__class__])
    r = await fastapi_client.get("/api/me")
    assert r.status_code == 401, r.text
    register_admin_model_class(UserModelAdmin, [tortoise_superuser.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_sign_out(tortoise_superuser, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)

    r = await fastapi_client.post(
        "/api/sign-out",
    )
    assert r.status_code == 200, r.text

    r = await fastapi_client.get(
        "/api/me",
    )
    assert r.status_code == 401, r.text

    r = await fastapi_client.post(
        "/api/sign-out",
    )
    assert r.status_code == 401, r.text
