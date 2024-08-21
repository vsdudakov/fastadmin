from django.db import models

from fastadmin import DjangoInlineModelAdmin, DjangoModelAdmin, WidgetType, action, display, register

EventTypeEnum = (
    ("PRIVATE", "PRIVATE"),
    ("PUBLIC", "PUBLIC"),
)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

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
class UserModelAdmin(DjangoModelAdmin):
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
    }

    def authenticate(self, username, password):
        obj = self.model_cls.objects.filter(username=username, is_superuser=True).first()
        if not obj:
            return None
        # if not obj.check_password(password):
        #     return None
        return obj.id

    def change_password(self, user_id, password):
        user = self.model_cls.objects.filter(id=user_id).first()
        if not user:
            return
        # direct saving password is only for tests - use hash
        user.password = password
        user.save()


class EventInlineModelAdmin(DjangoInlineModelAdmin):
    model = Event


@register(Tournament)
class TournamentModelAdmin(DjangoModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent)
class BaseEventModelAdmin(DjangoModelAdmin):
    pass


@register(Event)
class EventModelAdmin(DjangoModelAdmin):
    actions = ("make_is_active", "make_is_not_active")
    list_display = (
        "id",
        "name_with_price",
        "rating",
        "event_type",
        "is_active",
        "started",
    )

    @action(description="Make event active")
    def make_is_active(self, ids):
        self.model_cls.objects.filter(id__in=ids).update(is_active=True)

    @action
    def make_is_not_active(self, ids):
        self.model_cls.objects.filter(id__in=ids).update(is_active=False)

    @display
    def started(self, obj):
        return bool(obj.start_time)

    @display()
    def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"
