from enum import Enum

from tortoise import fields
from tortoise.models import Model

from fastadmin import TortoiseInlineModelAdmin, TortoiseModelAdmin, action, display, register


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @classmethod
    def get_model_name(cls):
        return f"tortoiseorm.{cls.__name__}"

    class Meta:
        abstract = True


class User(BaseModel):
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)

    async def __str__(self):
        return self.username

    class Meta:
        table = "user"


class Tournament(BaseModel):
    name = fields.CharField(max_length=255)

    async def __str__(self):
        return self.name

    class Meta:
        table = "tournament"


class BaseEvent(BaseModel):
    class Meta:
        table = "base_event"


class Event(BaseModel):
    base = fields.OneToOneField("models.BaseEvent", related_name="event", null=True, on_delete=fields.SET_NULL)
    name = fields.CharField(max_length=255)

    tournament = fields.ForeignKeyField("models.Tournament", related_name="events", on_delete=fields.CASCADE)
    participants = fields.ManyToManyField("models.User", related_name="events", through="event_participants")

    rating = fields.IntField(default=0)
    description = fields.TextField(null=True)
    event_type = fields.CharEnumField(EventTypeEnum, max_length=255, default=EventTypeEnum.PUBLIC)
    is_active = fields.BooleanField(default=True)
    start_time = fields.TimeField(null=True)
    date = fields.DateField(null=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

    json = fields.JSONField(null=True)

    async def __str__(self):
        return self.name

    class Meta:
        table = "event"


@register(User)
class TortoiseORMUserModelAdmin(TortoiseModelAdmin):
    model_name_prefix = "tortoiseorm"

    async def authenticate(self, username, password):
        obj = await self.model_cls.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id

    async def change_password(self, user_id, password):
        user = await self.model_cls.filter(id=user_id).first()
        if not user:
            return
        # direct saving password is only for tests - use hash
        user.password = password
        await user.save()


class TortoiseORMEventInlineModelAdmin(TortoiseInlineModelAdmin):
    model = Event
    model_name_prefix = "tortoiseorm"


@register(Tournament)
class TortoiseORMTournamentModelAdmin(TortoiseModelAdmin):
    inlines = (TortoiseORMEventInlineModelAdmin,)
    model_name_prefix = "tortoiseorm"


@register(BaseEvent)
class TortoiseORMBaseEventModelAdmin(TortoiseModelAdmin):
    model_name_prefix = "tortoiseorm"


@register(Event)
class TortoiseORMEventModelAdmin(TortoiseModelAdmin):
    model_name_prefix = "tortoiseorm"

    @action(description="Make user active")
    async def make_is_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=True)

    @action
    async def make_is_not_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=False)

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"
