from fastadmin.models.base import ModelAdmin


async def test_change_password(session_id, admin_models, user, client):
    assert session_id
    user_admin_model: ModelAdmin = admin_models[user.__class__]
    old_password = user.password
    r = await client.patch(
        f"/api/change-password/{user.id}",
        json={
            "password": "test",
            "confirm_password": "test",
        },
    )
    assert r.status_code == 200, r.text

    updated_user = await user_admin_model.get_obj(user.id)
    assert str(r.json()) == str(updated_user["id"])
    assert updated_user["password"] != old_password
    assert updated_user["password"] == "test"

    r = await client.patch(
        f"/api/change-password/{user.id}",
        json={
            "password": old_password,
            "confirm_password": old_password,
        },
    )
    assert r.status_code == 200, r.text


async def test_change_password_405(session_id, user, client):
    assert session_id
    r = await client.get(
        f"/api/change-password/{user.id}",
    )
    assert r.status_code == 405, r.text


async def test_change_password_401(user, client):
    r = await client.patch(
        f"/api/change-password/{user.id}",
        json={
            "password": "test",
            "confirm_password": "test",
        },
    )
    assert r.status_code == 401, r.text


async def test_change_password_404_obj_not_found(session_id, client):
    assert session_id
    r = await client.patch(
        "/api/change-password/invalid",
        json={
            "password": "test",
            "confirm_password": "test",
        },
    )
    assert r.status_code == 422, r.text

    r = await client.patch(
        "/api/change-password/-1",
        json={
            "password": "test",
            "confirm_password": "test",
        },
    )
    # we ignore
    assert r.status_code == 200, r.text
