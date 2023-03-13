from fastadmin.models.helpers import get_admin_model


async def test_add(session_id, admin_models, event, client):
    assert session_id
    event_admin_model = admin_models[event.__class__]
    fields = event_admin_model.get_model_fields()
    participant_admin_model = get_admin_model(fields["participants"]["parent_model"])
    participant = await participant_admin_model.save_model(None, {"username": "participant", "password": "test"})
    tournament_admin_model = get_admin_model(fields["tournament"]["parent_model"])
    tournament = await tournament_admin_model.save_model(None, {"name": "test_tournament"})

    r = await client.post(
        f"/api/add/{event.get_model_name()}",
        json={
            "name": "new name",
            "tournament_id": tournament["id"],
            "participants": [participant["id"]],
        },
    )
    assert r.status_code == 200, r.text
    item = r.json()
    updated_event = await event_admin_model.get_obj(item["id"])
    assert item["name"] == "new name"
    assert item["tournament_id"] == tournament["id"]
    assert item["created_at"] == updated_event["created_at"].isoformat()
    assert item["updated_at"] == updated_event["updated_at"].isoformat()
    assert item["participants"] == [participant["id"]]
    r = await client.delete(f"/api/delete/{event.get_model_name()}/{item['id']}")
    assert r.status_code == 200, r.text


async def test_add_405(session_id, event, client):
    assert session_id
    r = await client.get(
        f"/api/add/{event.get_model_name()}",
    )
    assert r.status_code == 405, r.text


async def test_add_401(superuser, tournament, event, client):
    r = await client.post(
        f"/api/add/{event.get_model_name()}",
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
        f"/api/add/{event.get_model_name()}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404, r.text
