import os
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

os.environ["ADMIN_USER_MODEL"] = "User"
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = "username"
os.environ["ADMIN_SECRET_KEY"] = "secret"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import BaseEvent, Event, Tournament, User, UserAttachment
from tortoise.contrib.fastapi import RegisterTortoise

from fastadmin import (
    TortoiseInlineModelAdmin,
    TortoiseModelAdmin,
    WidgetActionArgumentProps,
    WidgetActionChartProps,
    WidgetActionFilter,
    WidgetActionInputSchema,
    WidgetActionProps,
    WidgetActionResponseSchema,
    WidgetActionType,
    WidgetType,
    action,
    display,
)
from fastadmin import fastapi_app as admin_app
from fastadmin import (
    register,
    widget_action,
)


class UserAttachmentModelInline(TortoiseInlineModelAdmin):
    model = UserAttachment
    formfield_overrides = {  # noqa: RUF012
        "attachment_url": (
            WidgetType.UploadFile,
            {
                "required": True,
            },
        ),
    }

    async def upload_file(
        self,
        field_name: str,
        file_name: str,
        file_content: bytes,
    ) -> None:
        # save file to media directory or to s3/filestorage here
        return f"/media/{file_name}"


@register(User)
class UserModelAdmin(TortoiseModelAdmin):
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
        "avatar_url": (
            WidgetType.UploadImage,
            {
                "required": False,
                # Disable crop image for upload field
                # "disableCropImage": True,
            },
        ),
    }
    inlines = (UserAttachmentModelInline,)
    widget_actions = (
        "sales_chart",
        "sales_action",
    )

    async def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        obj = await self.model_cls.filter(username=username, password=password, is_superuser=True).first()
        if not obj:
            return None
        return obj.id

    async def change_password(self, id: uuid.UUID | int, password: str) -> None:
        user = await self.model_cls.filter(id=id).first()
        if not user:
            return
        # direct saving password is only for tests - use hash
        user.password = password
        await user.save()

    async def upload_file(
        self,
        field_name: str,
        file_name: str,
        file_content: bytes,
    ) -> None:
        # save file to media directory or to s3/filestorage here
        return f"/media/{file_name}"

    @widget_action(
        widget_action_type=WidgetActionType.ChartLine,
        widget_action_props=WidgetActionChartProps(x_field="x", y_field="y"),
        widget_action_filters=[
            WidgetActionFilter(
                field_name="x",
                widget_type=WidgetType.DatePicker,
            ),
            WidgetActionFilter(
                field_name="y",
                widget_type=WidgetType.Select,
                widget_props={
                    "options": [
                        {"label": "Sales", "value": "sales"},
                    ],
                },
            ),
        ],
        tab="Analytics",
        title="Sales over time",
        description="Line chart of sales",
        width=24,
    )
    async def sales_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {
                    "x": "2026-01-01",
                    "y": 100,
                },
                {
                    "x": "2026-01-02",
                    "y": 200,
                },
                {
                    "x": "2026-01-03",
                    "y": 300,
                },
            ],
        )

    @widget_action(
        widget_action_type=WidgetActionType.Action,
        widget_action_props=WidgetActionProps(
            arguments=[
                WidgetActionArgumentProps(
                    name="x",
                    widget_type=WidgetType.DatePicker,
                    widget_props={
                        "required": True,
                    },
                ),
            ],
        ),
        tab="Data",
        title="Get sales data",
        description="Get sales data",
        width=12,
    )
    async def sales_action(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {
                    "id": 1,
                    "name": "Sales",
                },
                {
                    "id": 2,
                    "name": "Sales",
                },
                {
                    "id": 3,
                    "name": "Sales",
                },
            ],
        )


class EventInlineModelAdmin(TortoiseInlineModelAdmin):
    model = Event


@register(Tournament)
class TournamentModelAdmin(TortoiseModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)
    widget_actions = ("tournament_action",)

    @widget_action(
        widget_action_type=WidgetActionType.Action,
        tab="Data",
        title="Get tournament data",
        description="Get tournament data",
        width=12,
    )
    async def tournament_action(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {
                    "id": 1,
                    "name": "Tournament 1",
                },
                {
                    "id": 2,
                    "name": "Tournament 2",
                },
                {
                    "id": 3,
                    "name": "Tournament 3",
                },
            ],
        )


@register(BaseEvent)
class BaseEventModelAdmin(TortoiseModelAdmin):
    pass


@register(Event)
class EventModelAdmin(TortoiseModelAdmin):
    actions = ("make_is_active", "make_is_not_active")
    list_display = (
        "id",
        "tournament_name",
        "name_with_price",
        "rating",
        "event_type",
        "is_active",
        "started",
        "start_time",
        "date",
    )
    list_filter = ("event_type", "is_active", "start_time", "date", "event_type")
    search_fields = ("name", "tournament__name")
    list_select_related = ("tournament",)

    @action(description="Make event active")
    async def make_is_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=True)

    @action
    async def make_is_not_active(self, ids):
        await self.model_cls.filter(id__in=ids).update(is_active=False)

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display
    async def tournament_name(self, obj):
        tournament = await obj.tournament
        return tournament.name

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"


async def create_superuser():
    await User.create(
        username="admin",
        password="admin",
        is_superuser=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # RegisterTortoise sets up TortoiseContext so request handlers can use the DB
    # (_enable_global_fallback=True by default for ASGI lifespan in a background task)
    async with RegisterTortoise(
        app=app,
        db_url="sqlite://:memory:",
        modules={"models": ["models"]},
        generate_schemas=True,
        use_tz=False,
        timezone="UTC",
    ):
        await create_superuser()
        yield


app = FastAPI(lifespan=lifespan)


app.mount("/admin", admin_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3030", "http://localhost:8090"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
