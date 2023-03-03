from fastadmin import TortoiseModelAdmin, register

from tests.tortoise.helpers import sign_in


async def test_retrieve(user, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, user)
    r = await client.get(
        f"/api/retrieve/{event.__class__.__name__}/{event.id}",
    )
    assert r.status_code == 200
    item = r.json()
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert "participants" in item
    assert item["participants"][0] == user.id
