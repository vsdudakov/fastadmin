from fastadmin import TortoiseModelAdmin, register

from tests.tortoise.helpers import sign_in
from fastadmin.models.helpers import unregister_admin_model


async def test_list(superuser, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, superuser)
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


async def test_list_401(superuser, tournament, event, client):
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 401


async def test_list_404(superuser, event, client):
    unregister_admin_model([event.__class__])
    await sign_in(client, superuser)
    r = await client.get(
        f"/api/list/{event.__class__.__name__}",
    )
    assert r.status_code == 404
