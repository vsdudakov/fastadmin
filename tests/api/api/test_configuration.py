from fastadmin import TortoiseModelAdmin, register

from tests.api.helpers import sign_in
from fastadmin.models.helpers import unregister_admin_model, register_admin_model


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
