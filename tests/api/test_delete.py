from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_delete(superuser, event, client):
    superuser = superuser
    event = event
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert item == event.id

    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_delete_401(event, client):
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 401, r.text


async def test_delete_404(superuser, event, client):
    unregister_admin_model_class([event.__class__])
    await sign_in(client, superuser)
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 404, r.text
    await sign_out(client, superuser)


async def test_delete_403(superuser, client):
    await sign_in(client, superuser)
    r = await client.delete(
        f"/api/delete/{superuser.__class__.__name__}/{superuser.id}",
    )
    assert r.status_code == 403, r.text
    await sign_out(client, superuser)
