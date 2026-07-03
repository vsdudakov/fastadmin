import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

os.environ["ADMIN_USER_MODEL"] = "User"
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = "username"
os.environ["ADMIN_SECRET_KEY"] = "secret"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import BaseEvent, Event, Tournament, User
from yara_orm import Model, YaraOrm

from fastadmin import (
    WidgetActionChartProps,
    WidgetActionFilter,
    WidgetActionInputSchema,
    WidgetActionResponseSchema,
    WidgetActionType,
    WidgetType,
    YaraOrmInlineModelAdmin,
    YaraOrmModelAdmin,
    action,
    display,
    register,
    widget_action,
)
from fastadmin import fastapi_app as admin_app


@register(User)
class UserModelAdmin(YaraOrmModelAdmin):
    menu_section = "Users"
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
        "avatar_url": (WidgetType.UploadImage, {"required": False}),
    }
    widget_actions = ("sales_chart",)

    async def authenticate(self, username: str, password: str) -> int | None:
        obj = await self.model_cls.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id

    async def change_password(self, id: int, password: str) -> None:
        user = await self.model_cls.filter(id=id).first()
        if not user:
            return
        # direct saving password is only for the example - hash it in production
        user.password = password
        await user.save()

    async def upload_file(
        self,
        field_name: str,
        file_name: str,
        file_content: bytes,
        obj: Model | None = None,
    ) -> str:
        # save file to a media directory or to s3/filestorage here
        return f"/media/{file_name}"

    @widget_action(
        widget_action_type=WidgetActionType.ChartLine,
        widget_action_props=WidgetActionChartProps(x_field="x", y_field="y", series_field="series"),
        widget_action_filters=[
            WidgetActionFilter(field_name="x", widget_type=WidgetType.DatePicker),
        ],
        tab="Analytics",
        title="Sales over time",
        description="Line chart of sales",
        width=24,
    )
    async def sales_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {"x": "2026-01-01", "y": 100, "series": "Sales"},
                {"x": "2026-01-02", "y": 200, "series": "Sales"},
            ],
        )


class EventInlineModelAdmin(YaraOrmInlineModelAdmin):
    model = Event


@register(Tournament)
class TournamentModelAdmin(YaraOrmModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent)
class BaseEventModelAdmin(YaraOrmModelAdmin):
    list_display = ("id", "name")


@register(Event)
class EventModelAdmin(YaraOrmModelAdmin):
    list_display = ("id", "name", "tournament", "is_active", "started")
    list_display_links = ("id", "name")
    list_filter = ("id", "name", "event_type", "is_active", "tournament")
    list_select_related = ("tournament",)
    search_fields = ("name",)
    actions = ("make_is_active", "make_is_not_active")

    @action(description="Make selected events active")
    async def make_is_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=True)

    @action(description="Make selected events inactive")
    async def make_is_not_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=False)

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"


async def create_superuser() -> None:
    if not await User.filter(username="admin").first():
        await User.create(username="admin", password="admin", is_superuser=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await YaraOrm.init("sqlite://:memory:")
    await YaraOrm.generate_schemas()
    await create_superuser()
    yield
    await YaraOrm.close()


app = FastAPI(lifespan=lifespan)

app.mount("/admin", admin_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3030", "http://localhost:8090"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
