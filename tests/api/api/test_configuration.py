from fastadmin.models.helpers import register_admin_model, unregister_admin_model
from tests.api.helpers import sign_in


async def test_configuration(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200
    data = r.json()
    assert data

    unregister_admin_model([event.__class__])


async def test_configuration_not_auth(objects, client):
    event = objects["event"]
    admin_event_cls = objects["admin_event_cls"]

    register_admin_model(admin_event_cls, [event.__class__])
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200
    data = r.json()
    assert data

    unregister_admin_model([event.__class__])


async def test_configuration_list_display(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]

    await sign_in(client, superuser, admin_user_cls)

    register_admin_model(admin_event_cls, [event.__class__])
    admin_event_cls.list_display = ["name"]
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200
    response_data = r.json()
    assert response_data

    unregister_admin_model([event.__class__])
