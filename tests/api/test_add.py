async def test_add(session_id, superuser, tournament, event, client):
    assert session_id
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 200, r.text
    item = r.json()
    event = await event.__class__.get(id=item["id"])
    assert item["name"] == "new name"
    assert item["tournament_id"] == tournament.id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert item["participants"] == [superuser.id]


async def test_add_405(session_id, event, client):
    assert session_id
    r = await client.get(
        f"/api/add/{event.__class__.__name__}",
    )
    assert r.status_code == 405, r.text


async def test_add_401(superuser, tournament, event, client):
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_add_404(session_id, admin_models, superuser, tournament, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404, r.text
