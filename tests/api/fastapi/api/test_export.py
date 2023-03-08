from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.fastapi.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_export(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])
    async with fastapi_client.stream(
        "POST",
        f"/api/export/{tortoise_event.__class__.__name__}",
        json={},
    ) as r:
        assert r.status_code == 200, r.text
        rows = []
        async for line in r.aiter_lines():
            rows.append(line)
    assert rows

    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_export_401(tortoise_event, fastapi_client):
    async with fastapi_client.stream(
        "POST",
        f"/api/export/{tortoise_event.__class__.__name__}",
        json={},
    ) as r:
        assert r.status_code == 401, r.text


async def test_export_404(tortoise_superuser, tortoise_event, fastapi_client):
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_in(fastapi_client, tortoise_superuser)
    async with fastapi_client.stream(
        "POST",
        f"/api/export/{tortoise_event.__class__.__name__}",
        json={},
    ) as r:
        assert r.status_code == 404, r.text
    await sign_out(fastapi_client, tortoise_superuser)
