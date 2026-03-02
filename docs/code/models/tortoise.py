from uuid import UUID

import bcrypt
from tortoise import fields
from tortoise.models import Model

from fastadmin import TortoiseModelAdmin, WidgetType, action, register, widget_action
from fastadmin.models.schemas import (
    WidgetActionArgumentProps,
    WidgetActionChartProps,
    WidgetActionFilter,
    WidgetActionInputSchema,
    WidgetActionProps,
    WidgetActionResponseSchema,
    WidgetActionType,
)


class ModelUser(Model):
    username = fields.CharField(max_length=255, unique=True)
    hash_password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=False)

    avatar_url = fields.TextField(null=True)

    def __str__(self):
        return self.username


@register(ModelUser)
class UserAdmin(TortoiseModelAdmin):
    list_display = ("username", "is_superuser", "is_active")
    list_display_links = ("username",)
    list_filter = (
        "username",
        "is_superuser",
        "is_active",
    )
    search_fields = (
        "id",
        "username",
    )
    fieldsets = (
        (None, {"fields": ("username", "hash_password")}),
        ("Permissions", {"fields": ("is_active", "is_superuser")}),
    )
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "hash_password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
        "avatar_url": (
            WidgetType.UploadImage,
            {
                "required": False,
                # "disableCropImage": True,  # optional: disable image cropping
            },
        ),
    }
    actions = (
        *TortoiseModelAdmin.actions,
        "activate",
        "deactivate",
    )
    widget_actions = (
        "users_chart",
        "users_action",
    )

    async def authenticate(self, username: str, password: str) -> int | None:
        user = await self.model_cls.filter(username=username, is_superuser=True).first()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return None
        return user.id

    async def change_password(self, id: UUID | int | str, password: str) -> None:
        user = await self.model_cls.filter(id=id).first()
        if not user:
            return
        user.hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        await user.save(update_fields=("hash_password",))

    @action(description="Set as active")
    async def activate(self, ids: list[int]) -> None:
        await self.model_cls.filter(id__in=ids).update(is_active=True)

    @action(description="Deactivate")
    async def deactivate(self, ids: list[int]) -> None:
        await self.model_cls.filter(id__in=ids).update(is_active=False)

    async def upload_file(self, field_name: str, file_name: str, file_content: bytes) -> str:
        # save file to media directory or s3/filestorage, then return the file url
        url = f"/media/{file_name}"
        return url

    @widget_action(
        widget_action_type=WidgetActionType.ChartLine,
        widget_action_props=WidgetActionChartProps(x_field="x", y_field="y"),
        widget_action_filters=[
            WidgetActionFilter(
                field_name="x",
                widget_type=WidgetType.DatePicker,
            ),
        ],
        tab="Analytics",
        title="Users over time",
        description="Line chart of active users over time",
        width=24,
    )
    async def users_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        # In a real project you would aggregate using payload.query filters.
        return WidgetActionResponseSchema(
            data=[
                {
                    "x": "2026-01-01",
                    "y": 10,
                },
                {
                    "x": "2026-01-02",
                    "y": 15,
                },
                {
                    "x": "2026-01-03",
                    "y": 7,
                },
            ],
        )

    @widget_action(
        widget_action_type=WidgetActionType.Action,
        widget_action_props=WidgetActionProps(
            arguments=[
                WidgetActionArgumentProps(
                    name="since",
                    widget_type=WidgetType.DatePicker,
                    widget_props={
                        "required": True,
                    },
                ),
            ],
        ),
        tab="Data",
        title="Export users",
        description="Return a simple table of users created since a date",
        width=12,
    )
    async def users_action(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {
                    "id": 1,
                    "username": "alice",
                },
                {
                    "id": 2,
                    "username": "bob",
                },
            ],
        )
