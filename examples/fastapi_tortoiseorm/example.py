from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import BaseEvent, Event, Tournament, User
from tortoise import Tortoise

from fastadmin import TortoiseInlineModelAdmin, TortoiseModelAdmin, WidgetType, action, display
from fastadmin import fastapi_app as admin_app
from fastadmin import register


@register(User)
class UserModelAdmin(TortoiseModelAdmin):
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
    }

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


class EventInlineModelAdmin(TortoiseInlineModelAdmin):
    model = Event


@register(Tournament)
class TournamentModelAdmin(TortoiseModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent)
class BaseEventModelAdmin(TortoiseModelAdmin):
    pass


@register(Event)
class EventModelAdmin(TortoiseModelAdmin):
    actions = ("make_is_active", "make_is_not_active")
    list_display = ("id", "name_with_price", "rating", "event_type", "is_active", "started")

    @action(description="Make event active")
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


app = FastAPI()


async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["models"]})
    await Tortoise.generate_schemas()


async def create_superuser():
    await User.create(
        username="admin",
        password="admin",
        is_superuser=True,
    )


@app.on_event("startup")
async def startup():
    await init_db()
    await create_superuser()


@app.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()


app.mount("/admin", admin_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
