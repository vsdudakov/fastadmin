async def test_action(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.actions = ("make_is_active",)
    await event_admin_model.save_model(event.id, {"is_active": False})
    r = await client.post(
        f"/api/action/{event.get_model_name()}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert not item
    updated_event = await event_admin_model.get_obj(event.id)
    assert updated_event["is_active"]


async def test_action_405(session_id, event, client):
    assert session_id
    r = await client.get(
        f"/api/action/{event.get_model_name()}/make_is_active",
    )
    assert r.status_code == 405, r.text


async def test_action_401(event, client):
    r = await client.post(
        f"/api/action/{event.get_model_name()}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_action_404(session_id, admin_models, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.post(
        f"/api/action/{event.get_model_name()}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 404, r.text


async def test_action_422(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.actions = ()
    await event_admin_model.save_model(event.id, {"is_active": False})
    r = await client.post(
        f"/api/action/{event.get_model_name()}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 422, r.text
    updated_event = await event_admin_model.get_obj(event.id)
    assert not updated_event["is_active"]

    event_admin_model.actions = ("invalid",)
    await event_admin_model.save_model(event.id, {"is_active": False})
    r = await client.post(
        f"/api/action/{event.get_model_name()}/invalid",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 422, r.text
    updated_event = await event_admin_model.get_obj(event.id)
    assert not updated_event["is_active"]
