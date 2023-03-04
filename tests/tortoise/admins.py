from fastadmin import TortoiseModelAdmin


class UserAdmin(TortoiseModelAdmin):
    async def authenticate(self, username, password):
        obj = await self.model_cls.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id


class TournamentAdmin(TortoiseModelAdmin):
    pass


class EventAdmin(TortoiseModelAdmin):
    pass
