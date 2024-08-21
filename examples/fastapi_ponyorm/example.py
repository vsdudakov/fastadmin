from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import BaseEvent, Event, Tournament, User, db
from pony.orm import commit, db_session

from fastadmin import PonyORMInlineModelAdmin, PonyORMModelAdmin, WidgetType, action, display
from fastadmin import fastapi_app as admin_app
from fastadmin import register


@register(User)
class UserModelAdmin(PonyORMModelAdmin):
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
    }

    @db_session
    def authenticate(self, username, password):
        obj = next((f for f in User.select(username=username, password=password, is_superuser=True)), None)  # fmt: skip
        if not obj:
            return None
        return obj.id

    @db_session
    def change_password(self, user_id, password):
        obj = next((f for f in self.model_cls.select(id=user_id)), None)
        if not obj:
            return
        # direct saving password is only for tests - use hash
        obj.password = password
        commit()


class EventInlineModelAdmin(PonyORMInlineModelAdmin):
    model = Event


@register(Tournament)
class TournamentModelAdmin(PonyORMModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent)
class BaseEventModelAdmin(PonyORMModelAdmin):
    pass


@register(Event)
class EventModelAdmin(PonyORMModelAdmin):
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
    @db_session
    def make_is_active(self, ids):
        # update(o.set(is_active=True) for o in self.model_cls if o.id in ids)
        objs = self.model_cls.select(lambda o: o.id in ids)
        for obj in objs:
            obj.is_active = True
        commit()

    @action
    @db_session
    def make_is_not_active(self, ids):
        # update(o.set(is_active=False) for o in self.model_cls if o.id in ids)
        objs = self.model_cls.select(lambda o: o.id in ids)
        for obj in objs:
            obj.is_active = False
        commit()

    @display
    @db_session
    def started(self, obj):
        return bool(obj.start_time)

    @display()
    @db_session
    def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"


def init_db():
    db.bind(provider="sqlite", filename=":sharedmemory:")
    db.generate_mapping(create_tables=True)


@db_session
def create_superuser():
    User(username="admin", password="admin", is_superuser=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    create_superuser()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/admin", admin_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
