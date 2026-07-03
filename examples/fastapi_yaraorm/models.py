from enum import Enum

from yara_orm import Model, fields


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)

    avatar_url = fields.TextField(null=True)

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
    name = fields.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        table = "base_event"


class Event(BaseModel):
    base = fields.OneToOneField("BaseEvent", related_name="event", null=True, on_delete="SET NULL")
    name = fields.CharField(max_length=255)

    tournament = fields.ForeignKeyField("Tournament", related_name="events", on_delete="CASCADE")
    participants = fields.ManyToManyField("User", related_name="events")

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

    def __str__(self):
        return self.name

    class Meta:
        table = "event"
