from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.fastapi.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_action(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])

    EventModelAdmin.actions = ("make_is_active",)
    tortoise_event.is_active = False
    await tortoise_event.save()
    r = await fastapi_client.post(
        f"/api/action/{tortoise_event.__class__.__name__}/make_is_active",
        json={
            "ids": [tortoise_event.id],
        },
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert not item
    tortoise_event = await tortoise_event.__class__.get(id=tortoise_event.id)
    assert tortoise_event.is_active

    EventModelAdmin.actions = ()
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_action_401(tortoise_event, fastapi_client):
    r = await fastapi_client.post(
        f"/api/action/{tortoise_event.__class__.__name__}/make_is_active",
        json={
            "ids": [tortoise_event.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_action_404(tortoise_superuser, tortoise_event, fastapi_client):
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_in(fastapi_client, tortoise_superuser)
    r = await fastapi_client.post(
        f"/api/action/{tortoise_event.__class__.__name__}/make_is_active",
        json={
            "ids": [tortoise_event.id],
        },
    )
    assert r.status_code == 404, r.text
    await sign_out(fastapi_client, tortoise_superuser)


async def test_action_422(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])

    EventModelAdmin.actions = ()
    tortoise_event.is_active = False
    await tortoise_event.save()
    r = await fastapi_client.post(
        f"/api/action/{tortoise_event.__class__.__name__}/make_is_active",
        json={
            "ids": [tortoise_event.id],
        },
    )
    assert r.status_code == 422, r.text
    item = r.json()
    assert item
    tortoise_event = await tortoise_event.__class__.get(id=tortoise_event.id)
    assert not tortoise_event.is_active

    EventModelAdmin.actions = ("invalid",)
    tortoise_event.is_active = False
    await tortoise_event.save()
    r = await fastapi_client.post(
        f"/api/action/{tortoise_event.__class__.__name__}/invalid",
        json={
            "ids": [tortoise_event.id],
        },
    )
    assert r.status_code == 422, r.text
    item = r.json()
    assert item
    tortoise_event = await tortoise_event.__class__.get(id=tortoise_event.id)
    assert not tortoise_event.is_active

    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)
