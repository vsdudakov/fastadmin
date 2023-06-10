from uuid import UUID

import bcrypt
from tortoise import fields
from tortoise.models import Model

from fastadmin import TortoiseModelAdmin, WidgetType, action, register


class ModelUser(Model):
    username = fields.CharField(max_length=255, unique=True)
    hash_password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=False)

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
    formfield_overrides = {
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
    }
    actions = (
        *TortoiseModelAdmin.actions,
        "activate",
        "deactivate",
    )

    async def authenticate(self, username: str, password: str) -> int | None:
        user = await self.model_cls.filter(phone=username, is_superuser=True).first()
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return None
        return user.id

    async def change_password(self, id: UUID | int, password: str) -> None:
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
