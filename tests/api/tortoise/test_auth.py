from tests.api.tortoise.helpers import sign_in
from fastadmin import TortoiseModelAdmin, register

from fastadmin.models.helpers import unregister_admin_model


async def test_api_sign_in_401_invalid_password(superuser, client):
    class UserAdmin(TortoiseModelAdmin):
        async def authenticate(self, username, password):
            obj = await superuser.__class__.filter(username=username, password=password, is_superuser=True).first()
            if not obj:
                return None
            return obj.id

    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": "invalid",
        }
    )
    assert r.status_code == 401


async def test_api_sign_in_401(superuser, client):
    class UserAdmin(TortoiseModelAdmin):
        async def authenticate(self, username, password):
            obj = await superuser.__class__.filter(username=username, password=password, is_superuser=True).first()
            if not obj:
                return None
            return obj.id

    unregister_admin_model([superuser.__class__])

    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": superuser.password,
        }
    )
    assert r.status_code == 401


async def test_api_sign_in(superuser, client):
    assert await sign_in(client, superuser)


async def test_api_me(superuser, client):
    await sign_in(client, superuser)

    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 200
    me = r.json()
    assert me["id"] == superuser.id
    assert me["username"] == superuser.username


async def test_api_sign_out(superuser, client):
    await sign_in(client, superuser)

    r = await client.post(
        "/api/sign-out",
    )
    assert r.status_code == 200

    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 401
