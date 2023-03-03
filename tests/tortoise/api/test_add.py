from fastadmin import TortoiseModelAdmin, register

from tests.tortoise.helpers import sign_in
from fastadmin.models.helpers import unregister_admin_model


async def test_add(superuser, tournament, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, superuser)
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        }
    )
    assert r.status_code == 200
    item = r.json()
    event = await event.__class__.get(id=item["id"])
    assert item["name"] ==  "new name"
    assert item["tournament_id"] == tournament.id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert item["participants"] == [superuser.id]


async def test_add_401(superuser, tournament, event, client):
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        }
    )
    assert r.status_code == 401


async def test_add_404(superuser, tournament, event, client):
    unregister_admin_model([event.__class__])
    await sign_in(client, superuser)
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [superuser.id],
        }
    )
    assert r.status_code == 404
