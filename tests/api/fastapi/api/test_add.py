from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.fastapi.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_add(tortoise_superuser, tortoise_tournament, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])
    r = await fastapi_client.post(
        f"/api/add/{tortoise_event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tortoise_tournament.id,
            "participants": [tortoise_superuser.id],
        },
    )
    assert r.status_code == 200, r.text
    item = r.json()
    tortoise_event = await tortoise_event.__class__.get(id=item["id"])
    assert item["name"] == "new name"
    assert item["tournament_id"] == tortoise_tournament.id
    assert item["created_at"] == tortoise_event.created_at.isoformat()
    assert item["updated_at"] == tortoise_event.updated_at.isoformat()
    assert item["participants"] == [tortoise_superuser.id]

    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_add_401(tortoise_superuser, tortoise_tournament, tortoise_event, fastapi_client):
    r = await fastapi_client.post(
        f"/api/add/{tortoise_event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tortoise_tournament.id,
            "participants": [tortoise_superuser.id],
        },
    )
    assert r.status_code == 401, r.text


async def test_add_404(tortoise_superuser, tortoise_tournament, tortoise_event, fastapi_client):
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_in(fastapi_client, tortoise_superuser)
    r = await fastapi_client.post(
        f"/api/add/{tortoise_event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tortoise_tournament.id,
            "participants": [tortoise_superuser.id],
        },
    )
    assert r.status_code == 404, r.text
    await sign_out(fastapi_client, tortoise_superuser)
