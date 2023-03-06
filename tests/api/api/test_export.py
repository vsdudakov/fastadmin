from fastadmin.models.helpers import register_admin_model, unregister_admin_model
from tests.api.helpers import sign_in, sign_out


async def test_export(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    admin_event_cls = objects["admin_event_cls"]
    await sign_in(client, superuser, admin_user_cls)
    register_admin_model(admin_event_cls, [event.__class__])
    async with client.stream(
        "POST",
        f"/api/export/{event.__class__.__name__}",
        json={},
    ) as r:
        assert r.status_code == 200, r.text
        rows = []
        async for line in r.aiter_lines():
            rows.append(line)
    assert rows

    unregister_admin_model([event.__class__])
    await sign_out(client, superuser)


async def test_export_401(objects, client):
    event = objects["event"]
    async with client.stream(
        "POST",
        f"/api/export/{event.__class__.__name__}",
        json={},
    ) as r:
        assert r.status_code == 401, r.text


async def test_export_404(objects, client):
    superuser = objects["superuser"]
    event = objects["event"]
    admin_user_cls = objects["admin_user_cls"]
    unregister_admin_model([event.__class__])
    await sign_in(client, superuser, admin_user_cls)
    async with client.stream(
        "POST",
        f"/api/export/{event.__class__.__name__}",
        json={},
    ) as r:
        assert r.status_code == 404, r.text
    await sign_out(client, superuser)
