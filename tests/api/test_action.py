async def test_action(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.actions = ("make_is_active",)
    event.is_active = False
    await event.save()
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert not item
    event = await event.__class__.get(id=event.id)
    assert event.is_active


async def test_action_405(session_id, event, client):
    assert session_id
    r = await client.get(
        f"/api/action/{event.__class__.__name__}/make_is_active",
    )
    assert r.status_code == 405, r.text


async def test_action_401(event, client):
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_action_404(session_id, admin_models, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 404, r.text


async def test_action_422(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    event_admin_model.actions = ()
    event.is_active = False
    await event.save()
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 422, r.text
    event = await event.__class__.get(id=event.id)
    assert not event.is_active

    event_admin_model.actions = ("invalid",)
    event.is_active = False
    await event.save()
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/invalid",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 422, r.text
    event = await event.__class__.get(id=event.id)
    assert not event.is_active
