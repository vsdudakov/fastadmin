from enum import Enum

from fastapi_admin.decorators import register
from fastapi_admin.models import TortoiseModelAdmin
from tortoise import Model, fields


class ModelPermission(str, Enum):
    Add = "Add"
    Change = "Change"
    Delete = "Delete"
    Export = "Export"


class Test1Model(Model):
    username = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    test_1_model = fields.ForeignKeyField("models.Test2Model", related_name="test_models")
    is_active = fields.BooleanField(default=True)
    permission = fields.CharEnumField(ModelPermission, max_length=255, null=True)


class Test2Model(Model):
    username = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)


class User(Model):
    username = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)


@register(User)
class UserAdmin(TortoiseModelAdmin):
    pass


@register(Test1Model)
class Test1Admin(TortoiseModelAdmin):
    list_display = ("username", "created_at", "test_1_model", "is_active", "permission")
    list_display_links = ("username",)
    list_filter = ("username", "created_at", "test_1_model", "is_active", "permission")
    list_per_page = 40
    radio_fields = ("permission",)
    sortable_by = ("created_at", "test_1_model", "is_active", "permission")
    search_help_text = "Search by username, created_at, test_1_model, is_active, permission"


@register(Test2Model)
class Test2Admin(TortoiseModelAdmin):
    pass
