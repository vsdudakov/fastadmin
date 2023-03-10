from enum import Enum

from tortoise import fields
from tortoise.contrib.postgres.fields import ArrayField
from tortoise.models import Model

from fastadmin import TortoiseInlineModelAdmin, TortoiseModelAdmin, action, display, register


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class TortoiseUser(BaseModel):
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)

    def __str__(self):
        return self.username


class TortoiseTournament(BaseModel):
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name


class TortoiseBaseEvent(BaseModel):
    pass


class TortoiseEvent(BaseModel):
    base = fields.OneToOneField("models.TortoiseBaseEvent", related_name="event", null=True)
    name = fields.CharField(max_length=255)

    tournament = fields.ForeignKeyField("models.TortoiseTournament", related_name="events")
    participants = fields.ManyToManyField("models.TortoiseUser", related_name="events")

    rating = fields.IntField(default=0)
    description = fields.TextField(null=True)
    event_type = fields.CharEnumField(EventTypeEnum, max_length=255, default=EventTypeEnum.PUBLIC)
    tags = ArrayField(element_type="text", null=True)
    is_active = fields.BooleanField(default=True)
    start_time = fields.TimeField(null=True)
    date = fields.DateField(null=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

    json = fields.JSONField(null=True)

    def __str__(self):
        return self.name


@register(TortoiseUser)
class TortoiseUserModelAdmin(TortoiseModelAdmin):
    async def authenticate(self, username, password):
        obj = await self.model_cls.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id


class TortoiseEventInlineModelAdmin(TortoiseInlineModelAdmin):
    model = TortoiseEvent
    fk_name = "tournament"


@register(TortoiseTournament)
class TortoiseTournamentModelAdmin(TortoiseModelAdmin):
    inlines = (TortoiseEventInlineModelAdmin,)


@register(TortoiseEvent)
class TortoiseEventModelAdmin(TortoiseModelAdmin):
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
