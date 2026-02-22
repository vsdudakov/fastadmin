import os
import typing as tp
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

os.environ["ADMIN_USER_MODEL"] = "User"
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = "username"
os.environ["ADMIN_SECRET_KEY"] = "secret"

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
        "avatar_url": (
            WidgetType.Upload,
            {
                "required": False,
                # Disable crop image for upload field
                # "disableCropImage": True,
            },
        ),
    }

    @db_session
    def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        obj = next((f for f in User.select(username=username, password=password, is_superuser=True)), None)  # fmt: skip
        if not obj:
            return None
        return obj.id

    @db_session
    def change_password(self, id: uuid.UUID | int, password: str) -> None:
        obj = next((f for f in self.model_cls.select(id=id)), None)
        if not obj:
            return
        # direct saving password is only for tests - use hash
        obj.password = password
        commit()

    @db_session
    def orm_save_upload_field(self, obj: tp.Any, field: str, base64: str) -> None:
        obj = next((f for f in self.model_cls.select(id=obj.id)), None)
        if not obj:
            return
        # convert base64 to bytes, upload to s3/filestorage, get url and save or save base64 as is to db (don't recommend it)
        setattr(obj, field, base64)
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
    list_display = ("id", "tournament", "name_with_price", "rating", "event_type", "is_active", "started")
    list_filter = ("tournament", "event_type", "is_active")
    search_fields = ("name", "tournament__name")

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
    # Use shared in-memory sqlite DB so tables are visible across connections/threads.
    db.bind(provider="sqlite", filename=":sharedmemory:", create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def create_superuser():
    User(username="admin", password="admin", is_superuser=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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
