async def test_change(session_id, superuser, event, client):
    assert session_id
    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/{event.id}",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 200, r.text

    event = await event.__class__.get(id=event.id)
    item = r.json()
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert item["participants"] == [superuser.id]


async def test_change_405(session_id, event, client):
    assert session_id
    r = await client.get(
        f"/api/change/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 405, r.text


async def test_change_401(superuser, event, client):
    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/{event.id}",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_change_404_admin_class_found(session_id, admin_models, superuser, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/{event.id}",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404, r.text


async def test_change_404_obj_not_found(session_id, superuser, event, client):
    assert session_id
    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/invalid",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 422, r.text

    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/-1",
        json={
            "name": "new name",
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404, r.text
