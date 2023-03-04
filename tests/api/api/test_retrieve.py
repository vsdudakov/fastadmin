from tests.api.helpers import sign_in, sign_out
from fastadmin.models.helpers import unregister_admin_model, register_admin_model


async def test_retrieve(objects, client):
    superuser = objects["superuser"]
    user = objects["user"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]
    await sign_in(client, superuser, admin_user_cls)
    register_admin_model(admin_event_cls, [event.__class__])
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200
    item = r.json()
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert "participants" in item
    assert item["participants"][0] == user.id

    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_retrieve_401(objects, client):
    event = objects["event"]
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 401


async def test_retrieve_404(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    await sign_in(client, superuser, admin_user_cls)
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 404
    await sign_out(client, superuser)
