from fastadmin import TortoiseModelAdmin, register

from tests.tortoise.helpers import sign_in


async def test_change(user, user_2, event, client):

    @register(event.__class__)
    class EventAdmin(TortoiseModelAdmin):
        pass

    await sign_in(client, user)
    r = await client.patch(
        f"/api/change/{event.__class__.__name__}/{event.id}",
        json={
            "name": "new name",
            "participants": [user_2.id],
        }
    )
    assert r.status_code == 200

    event = await event.__class__.get(id=event.id)
    item = r.json()
    assert item["id"] == event.id
    assert item["name"] == event.name
    assert item["tournament_id"] == event.tournament_id
    assert item["created_at"] == event.created_at.isoformat()
    assert item["updated_at"] == event.updated_at.isoformat()
    assert item["participants"] == [user_2.id]
