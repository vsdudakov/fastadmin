from fastadmin.models.helpers import register_admin_model, unregister_admin_model
from tests.api.helpers import sign_in, sign_out


async def test_list(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]
    await sign_in(client, superuser, admin_user_cls)
    register_admin_model(admin_event_cls, [event.__class__])
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 200
    data = r.json()
    assert data
    assert data["total"] == 1
    item = data["results"][0]
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert "participants" not in item  # no m2m2 fields on list

    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_list_401(objects, client):
    event = objects["event"]
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 401


async def test_list_404(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    await sign_in(client, superuser, admin_user_cls)
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 404
    await sign_out(client, superuser)
