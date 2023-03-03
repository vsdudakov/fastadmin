from tests.tortoise.helpers import sign_in


async def test_api_sign_in(user, client):
    assert await sign_in(client, user)


async def test_api_me(user, client):
    await sign_in(client, user)

    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 200
    me = r.json()
    assert me["id"] == user.id
    assert me["username"] == user.username


async def test_api_sign_out(user, client):
    await sign_in(client, user)

    r = await client.post(
        "/api/sign-out",
    )
    assert r.status_code == 200

    r = await client.get(
        "/api/me",
    )
    assert r.status_code == 401
