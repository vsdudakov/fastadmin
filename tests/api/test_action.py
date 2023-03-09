from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_action(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])

    EventModelAdmin.actions = ("make_is_active",)
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

    EventModelAdmin.actions = ()
    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_action_401(event, client):
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_action_404(superuser, event, client):
    unregister_admin_model_class([event.__class__])
    await sign_in(client, superuser)
    r = await client.post(
        f"/api/action/{event.__class__.__name__}/make_is_active",
        json={
            "ids": [event.id],
        },
    )
    assert r.status_code == 404, r.text
    await sign_out(client, superuser)


async def test_action_422(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])

    EventModelAdmin.actions = ()
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

    EventModelAdmin.actions = ("invalid",)
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

    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)
