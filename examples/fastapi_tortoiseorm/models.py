from enum import Enum

from tortoise import fields
from tortoise.models import Model


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

    def __str__(self):
        return self.username

    class Meta:
        table = "user"


class Tournament(BaseModel):
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        table = "tournament"


class BaseEvent(BaseModel):
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name

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
    start_time = fields.DatetimeField(null=True)
    date = fields.DateField(null=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

    json = fields.JSONField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        table = "event"
