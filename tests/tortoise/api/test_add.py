from fastadmin import TortoiseModelAdmin, register

from tests.tortoise.helpers import sign_in


async def test_change(user, tournament, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, user)
    r = await client.post(
        f"/api/add/{event.__class__.__name__}",
        json={
            "name": "new name",
            "tournament_id": tournament.id,
            "participants": [user.id],
        }
    )
    assert r.status_code == 200
    item = r.json()
    event = await event.__class__.get(id=item["id"])
    assert item["name"] ==  "new name"
    assert item["tournament_id"] == tournament.id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert item["participants"] == [user.id]
