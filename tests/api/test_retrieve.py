from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_retrieve(superuser, event, user, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200, r.text
    item = r.json()
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert "participants" in item
    assert item["participants"][0] == user.id

    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_retrieve_401(event, client):
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 401, r.text


async def test_retrieve_404_admin_class_found(superuser, event, client):
    unregister_admin_model_class([event.__class__])
    await sign_in(client, superuser)
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 404, r.text
    await sign_out(client, superuser)


async def test_retrieve_404_obj_not_found(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/invalid",
    )
    assert r.status_code == 422, r.text
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/-1",
    )
    assert r.status_code == 404, r.text
    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)
