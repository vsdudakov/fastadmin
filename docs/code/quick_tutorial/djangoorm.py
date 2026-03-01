import typing as tp

from django.db import models

from fastadmin import DjangoModelAdmin, register


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    hash_password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    avatar_url = models.ImageField(null=True)

    def __str__(self):
        return self.username


@register(User)
class UserAdmin(DjangoModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    def authenticate(self, username, password):
        obj = User.objects.filter(username=username, is_superuser=True).first()
        if not obj:
            return None
        if not obj.check_password(password):
            return None
        return obj.id

    def upload_file(self, obj: tp.Any, field_name: str, file_name: str, file_content: bytes) -> str:  # type: ignore[override]
        # save file to media directory or s3/filestorage, then return the file url
        return f"/media/{file_name}"
