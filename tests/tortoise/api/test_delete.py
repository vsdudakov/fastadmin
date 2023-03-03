from fastadmin import TortoiseModelAdmin, register

from tests.tortoise.helpers import sign_in


async def test_delete(user, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, user)
    r = await client.delete(
        f"/api/delete/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200
    item = r.json()
    assert item == str(event.id)
