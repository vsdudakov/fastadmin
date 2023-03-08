from fastadmin import TortoiseInlineModelAdmin, TortoiseModelAdmin, action, display

from .models import Event


class UserModelAdmin(TortoiseModelAdmin):
    async def authenticate(self, username, password):
        obj = await self.model_cls.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id


class EventInlineModelAdmin(TortoiseInlineModelAdmin):
    model = Event
    fk_name = "tournament"


class TournamentModelAdmin(TortoiseModelAdmin):
    inlines = (EventInlineModelAdmin,)


class EventModelAdmin(TortoiseModelAdmin):
    @action(description="Make user active")
    async def make_is_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=True)

    @action
    async def make_is_not_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=True)

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"
