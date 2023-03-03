from fastadmin.models.helpers import register_admin_model
from fastadmin import TortoiseModelAdmin


async def sign_in(client, user):
    class UserAdmin(TortoiseModelAdmin):
        async def authenticate(self, username, password):
            return await user.__class__.filter(username=username, password=password).first()

    register_admin_model(UserAdmin, [user.__class__])

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
