from fastadmin.models.helpers import register_admin_model, unregister_admin_model
from tests.api.helpers import sign_in, sign_out


async def test_action(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]
    await sign_in(client, superuser, admin_user_cls)
    register_admin_model(admin_event_cls, [event.__class__])

    admin_event_cls.actions = ("make_is_active",)
    event.is_active = False
    await event.save()
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert not item
    event = await event.__class__.get(id=event.id)
    assert event.is_active

    admin_event_cls.actions = ()
    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_action_401(objects, client):
    event = objects["event"]
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_action_404(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    unregister_admin_model([event.__class__])
    await sign_in(client, superuser, admin_user_cls)
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 404, r.text
    await sign_out(client, superuser)


async def test_action_422(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]
    await sign_in(client, superuser, admin_user_cls)
    register_admin_model(admin_event_cls, [event.__class__])

    admin_event_cls.actions = ()
    event.is_active = False
    await event.save()
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 422, r.text
    item = r.json()
    assert item
    event = await event.__class__.get(id=event.id)
    assert not event.is_active

    admin_event_cls.actions = ("invalid",)
    event.is_active = False
    await event.save()
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/invalid",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 422, r.text
    item = r.json()
    assert item
    event = await event.__class__.get(id=event.id)
    assert not event.is_active

    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)
