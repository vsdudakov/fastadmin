from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.fastapi.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_delete(tortoise_superuser, tortoise_event, fastapi_client):
    superuser = tortoise_superuser
    event = tortoise_event
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])
    r = await fastapi_client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert item == event.id

    unregister_admin_model_class([event.__class__])
    await sign_out(fastapi_client, superuser)


async def test_delete_401(tortoise_event, fastapi_client):
    r = await fastapi_client.delete(
        f"/api/delete/{tortoise_event.__class__.__name__}/{tortoise_event.id}",
    )
    assert r.status_code == 401, r.text


async def test_delete_404(tortoise_superuser, tortoise_event, fastapi_client):
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_in(fastapi_client, tortoise_superuser)
    r = await fastapi_client.delete(
        f"/api/delete/{tortoise_event.__class__.__name__}/{tortoise_event.id}",
    )
    assert r.status_code == 404, r.text
    await sign_out(fastapi_client, tortoise_superuser)


async def test_delete_403(tortoise_superuser, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    r = await fastapi_client.delete(
        f"/api/delete/{tortoise_superuser.__class__.__name__}/{tortoise_superuser.id}",
    )
    assert r.status_code == 403, r.text
    await sign_out(fastapi_client, tortoise_superuser)
