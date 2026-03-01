import uuid

import bcrypt
from pony.orm import Database, LongStr, Optional, PrimaryKey, Required, commit, db_session

from fastadmin import PonyORMModelAdmin, WidgetType, register

db = Database()
db.bind(provider="sqlite", filename=":memory:", create_db=True)


class User(db.Entity):  # type: ignore [name-defined]
    _table_ = "user"
    id = PrimaryKey(int, auto=True)
    username = Required(str)
    hash_password = Required(str)
    is_superuser = Required(bool, default=False)
    is_active = Required(bool, default=False)
    avatar_url = Optional(LongStr, nullable=True)

    def __str__(self):
        return self.username


@register(User)
class UserAdmin(PonyORMModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "avatar_url": (WidgetType.UploadImage, {"required": False}),
    }

    @db_session
    def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        obj = next((f for f in User.select(username=username, password=password, is_superuser=True)), None)  # fmt: skip
        if not obj:
            return None
        if not bcrypt.checkpw(password.encode(), obj.hash_password.encode()):
            return None
        return obj.id

    @db_session
    def change_password(self, id: uuid.UUID | int, password: str) -> None:
        obj = next((f for f in self.model_cls.select(id=id)), None)
        if not obj:
            return
        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        obj.hash_password = hash_password
        commit()

    def upload_file(self, field_name: str, file_name: str, file_content: bytes) -> str:  # type: ignore[override]
        # save file to media directory or s3/filestorage, then return the file url
        return f"/media/{file_name}"
