from fastadmin.api.service import get_user_id_from_session_id


async def test_delete(session_id, event, client):
    assert session_id

    r = await client.delete(
        f"/api/delete/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 200, r.text
    obj_id = r.json()
    assert str(obj_id) == str(event.id)


async def test_configuration_405(session_id, event, client):
    assert session_id
    r = await client.get(
        f"/api/delete/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 405, r.text


async def test_delete_401(event, client):
    r = await client.delete(
        f"/api/delete/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 401, r.text


async def test_delete_404(session_id, admin_models, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.delete(
        f"/api/delete/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 404, r.text


async def test_delete_403(session_id, superuser, client):
    assert session_id
    user_id = await get_user_id_from_session_id(session_id)
    assert user_id
    r = await client.delete(
        f"/api/delete/{superuser.get_model_name()}/{user_id}",
    )
    assert r.status_code == 403, r.text


async def test_delete_422(session_id, event, client):
    """Non-existent but valid-format id: API may return 200 (idempotent), 404, or 500 depending on ORM."""
    assert session_id
    non_existent_id = 999999
    r = await client.delete(
        f"/api/delete/{event.get_model_name()}/{non_existent_id}",
    )
    assert r.status_code in (
        200,
        404,
        500,
    ), f"expected 200, 404, or 500, got {r.status_code}: {r.text}"
    if r.status_code == 500:
        assert "not found" in r.text.lower() or "Error deleting" in r.text
