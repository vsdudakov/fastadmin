from fastadmin.models.helpers import register_admin_model, unregister_admin_model


async def sign_in(client, user, admin_user_cls):
    register_admin_model(admin_user_cls, [user.__class__])
    r = await client.post(
        "/api/sign-in",
        json={
            "username": user.username,
            "password": user.password,
        },
    )
    assert r.status_code == 200
    assert r.json() is None
    return r.cookies


async def sign_out(client, user):
    r = await client.post("/api/sign-out")
    assert r.status_code == 200
    assert r.json() is None
    unregister_admin_model([user.__class__])
