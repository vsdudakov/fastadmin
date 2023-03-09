from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_add(superuser, tournament, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])
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

    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


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


async def test_add_404(superuser, tournament, event, client):
    unregister_admin_model_class([event.__class__])
    await sign_in(client, superuser)
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        },
    )
    assert r.status_code == 404, r.text
    await sign_out(client, superuser)
