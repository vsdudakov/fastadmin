from asgiref.sync import sync_to_async
from django.db import models

from fastadmin import DjangoInlineModelAdmin, DjangoModelAdmin, action, display, register

EventTypeEnum = (
    ("PRIVATE", "PRIVATE"),
    ("PUBLIC", "PUBLIC"),
)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_model_name(cls):
        return f"django.{cls.__name__}"

    class Meta:
        abstract = True


class User(BaseModel):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"


class Tournament(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tournament"


class BaseEvent(BaseModel):
    class Meta:
        db_table = "base_event"


class Event(BaseModel):
    base = models.OneToOneField(BaseEvent, related_name="event", null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)

    tournament = models.ForeignKey(Tournament, related_name="events", on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name="events")

    rating = models.IntegerField(default=0)
    description = models.TextField(null=True)
    event_type = models.CharField(max_length=255, default="PUBLIC", choices=EventTypeEnum)
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField(null=True)
    date = models.DateField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    json = models.JSONField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "event"


@register(User)
class DjangoUserModelAdmin(DjangoModelAdmin):
    model_name_prefix = "django"

    @sync_to_async
    def _authenticate(self, username, password):
        obj = self.model_cls.objects.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id

    async def authenticate(self, username, password):
        return await self._authenticate(username, password)


class DjangoEventInlineModelAdmin(DjangoInlineModelAdmin):
    model = Event
    model_name_prefix = "django"
    fk_name = "tournament"


@register(Tournament)
class DjangoTournamentModelAdmin(DjangoModelAdmin):
    model_name_prefix = "django"
    inlines = (DjangoEventInlineModelAdmin,)


@register(Event)
class DjangoEventModelAdmin(DjangoModelAdmin):
    model_name_prefix = "django"

    @sync_to_async
    def _make_is_active(self, ids):
        self.model_cls.objects.filter(id__in=ids).update(is_active=True)

    @sync_to_async
    def _make_is_not_active(self, ids):
        self.model_cls.objects.filter(id__in=ids).update(is_active=False)

    @action(description="Make user active")
    async def make_is_active(self, ids):
        await self._make_is_active(ids)

    @action
    async def make_is_not_active(self, ids):
        await self._make_is_not_active(ids)

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"
