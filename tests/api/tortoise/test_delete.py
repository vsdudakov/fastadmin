from fastadmin import TortoiseModelAdmin, register

from tests.api.tortoise.helpers import sign_in
from fastadmin.models.helpers import unregister_admin_model


async def test_delete(superuser, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, superuser)
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200
    item = r.json()
    assert item == str(event.id)


async def test_delete_401(superuser, tournament, event, client):
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 401


async def test_delete_404(superuser, event, client):
    unregister_admin_model([event.__class__])
    await sign_in(client, superuser)
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 404
