from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_export(superuser, event, client):
    await sign_in(client, superuser)
    register_admin_model_class(EventModelAdmin, [event.__class__])
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

    unregister_admin_model_class([event.__class__])
    await sign_out(client, superuser)


async def test_export_401(event, client):
    async with client.stream(
        "POST",
        f"/api/export/{event.__class__.__name__}",
        json={},
    ) as r:
        assert r.status_code == 401, r.text


async def test_export_404(superuser, event, client):
    unregister_admin_model_class([event.__class__])
    await sign_in(client, superuser)
    async with client.stream(
        "POST",
        f"/api/export/{event.__class__.__name__}",
        json={},
    ) as r:
        assert r.status_code == 404, r.text
    await sign_out(client, superuser)
