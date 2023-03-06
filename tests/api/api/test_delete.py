from fastadmin.models.helpers import register_admin_model, unregister_admin_model
from tests.api.helpers import sign_in, sign_out


async def test_delete(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]
    await sign_in(client, superuser, admin_user_cls)
    register_admin_model(admin_event_cls, [event.__class__])
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert item == event.id

    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_delete_401(objects, client):
    event = objects["event"]
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 401, r.text


async def test_delete_404(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    unregister_admin_model([event.__class__])
    await sign_in(client, superuser, admin_user_cls)
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 404, r.text
    await sign_out(client, superuser)


async def test_delete_403(objects, client):
    superuser = objects["superuser"]
    admin_user_cls = objects["admin_user_cls"]
    await sign_in(client, superuser, admin_user_cls)
    r = await client.delete(
        f"/api/delete/{superuser.__class__.__name__}/{superuser.id}",
    )
    assert r.status_code == 403, r.text
    await sign_out(client, superuser)
