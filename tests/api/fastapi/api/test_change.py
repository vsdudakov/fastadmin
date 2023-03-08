from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.fastapi.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_change(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])
    r = await fastapi_client.patch(
        f"/api/change/{tortoise_event.__class__.__name__}/{tortoise_event.id}",
        json={
            "name": "new name",
            "participants": [tortoise_superuser.id],
        },
    )
    assert r.status_code == 200, r.text

    tortoise_event = await tortoise_event.__class__.get(id=tortoise_event.id)
    item = r.json()
    assert item["id"] == tortoise_event.id
    assert item["name"] == tortoise_event.name
    assert item["tournament_id"] == tortoise_event.tournament_id
    assert item["created_at"] == tortoise_event.created_at.isoformat()
    assert item["updated_at"] == tortoise_event.updated_at.isoformat()
    assert item["participants"] == [tortoise_superuser.id]

    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_change_401(tortoise_superuser, tortoise_event, fastapi_client):
    r = await fastapi_client.patch(
        f"/api/change/{tortoise_event.__class__.__name__}/{tortoise_event.id}",
        json={
            "name": "new name",
            "participants": [tortoise_superuser.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_change_404_admin_class_found(tortoise_superuser, tortoise_event, fastapi_client):
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_in(fastapi_client, tortoise_superuser)
    r = await fastapi_client.patch(
        f"/api/change/{tortoise_event.__class__.__name__}/{tortoise_event.id}",
        json={
            "name": "new name",
            "participants": [tortoise_superuser.id],
        },
    )
    assert r.status_code == 404, r.text
    await sign_out(fastapi_client, tortoise_superuser)


async def test_change_404_obj_not_found(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])
    r = await fastapi_client.patch(
        f"/api/change/{tortoise_event.__class__.__name__}/invalid",
        json={
            "name": "new name",
            "participants": [tortoise_superuser.id],
        },
    )
    assert r.status_code == 422, r.text

    r = await fastapi_client.patch(
        f"/api/change/{tortoise_event.__class__.__name__}/-1",
        json={
            "name": "new name",
            "participants": [tortoise_superuser.id],
        },
    )
    assert r.status_code == 404, r.text

    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)
