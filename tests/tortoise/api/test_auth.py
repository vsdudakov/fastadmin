from fastadmin import TortoiseModelAdmin, register


async def test_api_sign_in(user, client):

    @register(user.__class__)
    class UserAdmin(TortoiseModelAdmin):
        async def authenticate(self, username, password):
            return await user.__class__.filter(username=username, password=password).first()

    r = await client.post(
        "/api/sign-in",
        json={
            "username": user.username,
            "password": "password",
        }
    )
    assert r.status_code == 200
    assert r.json() is None
