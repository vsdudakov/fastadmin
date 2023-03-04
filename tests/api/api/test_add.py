from fastadmin.models.helpers import register_admin_model, unregister_admin_model
from tests.api.helpers import sign_in, sign_out


async def test_add(objects, client):
    superuser = objects["superuser"]
    tournament = objects["tournament"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]
    await sign_in(client, superuser, admin_user_cls)
    register_admin_model(admin_event_cls, [event.__class__])
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 200
    item = r.json()
    event = await event.__class__.get(id=item["id"])
    assert item["name"] == "new name"
    assert item["tournament_id"] == tournament.id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert item["participants"] == [superuser.id]

    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_add_401(objects, client):
    superuser = objects["superuser"]
    tournament = objects["tournament"]
    event = objects["event"]
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 401


async def test_add_404(objects, client):
    superuser = objects["superuser"]
    tournament = objects["tournament"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    unregister_admin_model([event.__class__])
    await sign_in(client, superuser, admin_user_cls)
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404
    await sign_out(client, superuser)
