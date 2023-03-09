from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.models.orms.tortoise.admins import UserModelAdmin


async def sign_in(client, user):
    register_admin_model_class(UserModelAdmin, [user.__class__])
    r = await client.post(
        "/api/sign-in",
        json={
            "username": user.username,
            "password": user.password,
        },
    )
    assert r.status_code == 200, r.status_code
    assert not r.json(), r.json()
    return r.cookies


async def sign_out(client, user):
    r = await client.post("/api/sign-out")
    assert r.status_code == 200, r.status_code
    assert not r.json(), r.json()
    unregister_admin_model_class([user.__class__])


async def request(client, method, url, json=None, cookies=None):
    return await client.request(method, url, json=json, cookies=cookies)
