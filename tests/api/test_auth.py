from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import UserModelAdmin


async def test_sign_in_401_invalid_password(superuser, client):
    register_admin_model_class(UserModelAdmin, [superuser.__class__])
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": "invalid",
        },
    )
    assert r.status_code == 401, r.text
    unregister_admin_model_class([superuser.__class__])


async def test_sign_in_401(superuser, client):
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": superuser.password,
        },
    )
    assert r.status_code == 401, r.text


async def test_sign_in(superuser, client):
    assert await sign_in(client, superuser)
    await sign_out(client, superuser)


async def test_me(superuser, client):
    await sign_in(client, superuser)

    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 200, r.text
    me = r.json()
    assert me["id"] == superuser.id
    assert me["username"] == superuser.username
    await sign_out(client, superuser)


async def test_me_401(client):
    r = await client.get("/api/me")
    assert r.status_code == 401, r.text


async def test_me_404(superuser, client):
    await sign_in(client, superuser)
    unregister_admin_model_class([superuser.__class__])
    r = await client.get("/api/me")
    assert r.status_code == 401, r.text
    register_admin_model_class(UserModelAdmin, [superuser.__class__])
    await sign_out(client, superuser)


async def test_sign_out(superuser, client):
    await sign_in(client, superuser)

    r = await client.post(
        "/api/sign-out",
    )
    assert r.status_code == 200, r.text

    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 401, r.text

    r = await client.post(
        "/api/sign-out",
    )
    assert r.status_code == 401, r.text
