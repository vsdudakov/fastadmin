async def test_retrieve(session_id, event, user, client):
    assert session_id

    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert "participants" in item
    assert item["participants"][0] == user.id


async def test_list_405(session_id, event, client):
    assert session_id
    r = await client.post(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 405, r.text


async def test_retrieve_401(event, client):
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 401, r.text


async def test_retrieve_404_admin_class_found(session_id, admin_models, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 404, r.text


async def test_retrieve_404_obj_not_found(session_id, event, client):
    assert session_id

    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/invalid",
    )
    assert r.status_code == 422, r.text
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/-1",
    )
    assert r.status_code == 404, r.text
