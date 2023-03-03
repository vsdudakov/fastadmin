from fastadmin import TortoiseModelAdmin, register


async def sign_in(client, user):

    @register(user.__class__)
    class UserAdmin(TortoiseModelAdmin):
        async def authenticate(self, username, password):
            obj = await user.__class__.filter(username=username, password=password, is_superuser=True).first()
            if not obj:
                return None
            return obj.id

    r = await client.post(
        "/api/sign-in",
        json={
            "username": user.username,
            "password": user.password,
        }
    )
    assert r.status_code == 200
    assert r.json() is None
    return r.cookies
