from fastadmin.api.service import get_user_id_from_session_id
from fastadmin.settings import settings


async def test_sign_in_401_invalid_password(superuser, client):
    settings.ADMIN_USER_MODEL = superuser.get_model_name()
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": "invalid",
        },
    )
    assert r.status_code == 401, r.text


async def test_sign_in_401(superuser, admin_models, client):
    settings.ADMIN_USER_MODEL = superuser.get_model_name()
    del admin_models[superuser.__class__]
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": superuser.password,
        },
    )
    assert r.status_code == 401, r.text


async def test_sign_in_405(client):
    r = await client.get("/api/sign-in")
    assert r.status_code == 405, r.text


async def test_sign_in(superuser, client):
    settings.ADMIN_USER_MODEL = superuser.get_model_name()
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": superuser.password,
        },
    )
    assert r.status_code == 200, r.text


async def test_me(session_id, client):
    assert session_id
    user_id = await get_user_id_from_session_id(session_id)
    assert user_id
    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 200, r.text
    me = r.json()
    assert str(me["id"]) == str(user_id)


async def test_me_401(client):
    r = await client.get("/api/me")
    assert r.status_code == 401, r.text


async def test_me_405(session_id, client):
    assert session_id
    r = await client.post("/api/me")
    assert r.status_code == 405, r.text


async def test_me_404(session_id, admin_models, superuser, client):
    assert session_id
    settings.ADMIN_USER_MODEL = superuser.get_model_name()
    del admin_models[superuser.__class__]
    r = await client.get("/api/me")
    assert r.status_code == 401, r.text


async def test_sign_out(superuser, client):
    settings.ADMIN_USER_MODEL = superuser.get_model_name()
    r = await client.post(
        "/api/sign-in",
        json={
            "username": superuser.username,
            "password": superuser.password,
        },
    )
    assert r.status_code == 200, r.status_code

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


async def test_sign_out_405(session_id, client):
    assert session_id
    r = await client.get("/api/sign-out")
    assert r.status_code == 405, r.text
