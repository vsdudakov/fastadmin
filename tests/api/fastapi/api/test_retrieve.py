from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.fastapi.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_retrieve(tortoise_superuser, tortoise_event, tortoise_user, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])
    r = await fastapi_client.get(
        f"/api/retrieve/{tortoise_event.__class__.__name__}/{tortoise_event.id}",
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert item["id"] == tortoise_event.id
    assert item["name"] == tortoise_event.name
    assert item["tournament_id"] == tortoise_event.tournament_id
    assert item["created_at"] == tortoise_event.created_at.isoformat()
    assert item["updated_at"] == tortoise_event.updated_at.isoformat()
    assert "participants" in item
    assert item["participants"][0] == tortoise_user.id

    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_retrieve_401(tortoise_event, fastapi_client):
    r = await fastapi_client.get(
        f"/api/retrieve/{tortoise_event.__class__.__name__}/{tortoise_event.id}",
    )
    assert r.status_code == 401, r.text


async def test_retrieve_404_admin_class_found(tortoise_superuser, tortoise_event, fastapi_client):
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_in(fastapi_client, tortoise_superuser)
    r = await fastapi_client.get(
        f"/api/retrieve/{tortoise_event.__class__.__name__}/{tortoise_event.id}",
    )
    assert r.status_code == 404, r.text
    await sign_out(fastapi_client, tortoise_superuser)


async def test_retrieve_404_obj_not_found(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])
    r = await fastapi_client.get(
        f"/api/retrieve/{tortoise_event.__class__.__name__}/invalid",
    )
    assert r.status_code == 422, r.text
    r = await fastapi_client.get(
        f"/api/retrieve/{tortoise_event.__class__.__name__}/-1",
    )
    assert r.status_code == 404, r.text
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)
