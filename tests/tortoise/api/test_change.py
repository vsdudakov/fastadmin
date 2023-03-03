from fastadmin import TortoiseModelAdmin, register

from tests.tortoise.helpers import sign_in
from fastadmin.models.helpers import unregister_admin_model


async def test_change(superuser, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, superuser)
    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/{event.id}",
        json={
            "name": "new name",
            "participants": [superuser.id],
        }
    )
    assert r.status_code == 200

    event = await event.__class__.get(id=event.id)
    item = r.json()
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert item["participants"] == [superuser.id]


async def test_change_401(superuser, tournament, event, client):
    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/{event.id}",
        json={
            "name": "new name",
            "participants": [superuser.id],
        }
    )
    assert r.status_code == 401


async def test_change_404(superuser, event, client):
    unregister_admin_model([event.__class__])
    await sign_in(client, superuser)
    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/{event.id}",
        json={
            "name": "new name",
            "participants": [superuser.id],
        }
    )
    assert r.status_code == 404
