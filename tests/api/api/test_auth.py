from tests.api.helpers import sign_in, sign_out
from fastadmin.models.helpers import unregister_admin_model, register_admin_model


async def test_sign_in_401_invalid_password(objects, client):
    superuser = objects["superuser"]
    admin_user_cls = objects["admin_user_cls"]
    register_admin_model(admin_user_cls, [superuser.__class__])
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": "invalid",
        }
    )
    assert r.status_code == 401
    unregister_admin_model([superuser.__class__])


async def test_sign_in_401(objects, client):
    superuser = objects["superuser"]
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": superuser.password,
        }
    )
    assert r.status_code == 401


async def test_sign_in(objects, client):
    superuser = objects["superuser"]
    admin_user_cls = objects["admin_user_cls"]
    assert await sign_in(client, superuser, admin_user_cls)
    await sign_out(client, superuser)


async def test_me(objects, client):
    superuser = objects["superuser"]
    admin_user_cls = objects["admin_user_cls"]
    await sign_in(client, superuser, admin_user_cls)

    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 200
    me = r.json()
    assert me["id"] == superuser.id
    assert me["username"] == superuser.username
    await sign_out(client, superuser)


async def test_me_401(client):
    r = await client.get("/api/me")
    assert r.status_code == 401


async def test_me_404(objects, client):
    superuser = objects["superuser"]
    admin_user_cls = objects["admin_user_cls"]
    await sign_in(client, superuser, admin_user_cls)
    unregister_admin_model([superuser.__class__])
    r = await client.get("/api/me")
    assert r.status_code == 401
    register_admin_model(admin_user_cls, [superuser.__class__])
    await sign_out(client, superuser)


async def test_sign_out(objects, client):
    superuser = objects["superuser"]
    admin_user_cls = objects["admin_user_cls"]
    await sign_in(client, superuser, admin_user_cls)

    r = await client.post(
        "/api/sign-out",
    )
    assert r.status_code == 200

    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 401

    r = await client.post(
        "/api/sign-out",
    )
    assert r.status_code == 401
