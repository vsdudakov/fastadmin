import datetime


async def test_retrieve(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]

    r = await client.get(
        f"/api/retrieve/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 200, r.text
    item = r.json()
    updated_event = await event_admin_model.get_obj(event.id)
    assert item["id"] == updated_event["id"]
    assert item["name"] == updated_event["name"]
    assert item["tournament"] == updated_event["tournament"]
    assert datetime.datetime.fromisoformat(item["created_at"]) == updated_event["created_at"]
    assert datetime.datetime.fromisoformat(item["updated_at"]) == updated_event["updated_at"]
    assert "participants" in item
    assert item["participants"]
    assert item["participants"][0] == updated_event["participants"][0]


async def test_list_405(session_id, event, client):
    assert session_id
    r = await client.post(
        f"/api/retrieve/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 405, r.text


async def test_retrieve_401(event, client):
    r = await client.get(
        f"/api/retrieve/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 401, r.text


async def test_retrieve_404_admin_class_found(session_id, admin_models, event, client):
    assert session_id
    del admin_models[event.__class__]
    r = await client.get(
        f"/api/retrieve/{event.get_model_name()}/{event.id}",
    )
    assert r.status_code == 404, r.text


async def test_retrieve_404_obj_not_found(session_id, event, client):
    assert session_id

    # "invalid" is valid as string PK; lookup fails → 404
    r = await client.get(
        f"/api/retrieve/{event.get_model_name()}/invalid",
    )
    assert r.status_code == 404, r.text
    r = await client.get(
        f"/api/retrieve/{event.get_model_name()}/-1",
    )
    assert r.status_code == 404, r.text
