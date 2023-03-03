from fastadmin import TortoiseModelAdmin, register

from tests.tortoise.helpers import sign_in


async def test_configuration(superuser, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, superuser)
    r = await client.get(
        f"/api/configuration",
    )
    assert r.status_code == 200
    data = r.json()
    assert data
