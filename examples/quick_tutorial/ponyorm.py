import bcrypt
from pony.orm import Database, PrimaryKey, Required, db_session

from fastadmin import PonyORMModelAdmin, register

db = Database()
db.bind(provider="sqlite", filename=":memory:", create_db=True)


class User(db.Entity):  # type: ignore [name-defined]
    _table_ = "user"
    id = PrimaryKey(int, auto=True)
    username = Required(str)
    hash_password = Required(str)
    is_superuser = Required(bool, default=False)
    is_active = Required(bool, default=False)

    def __str__(self):
        return self.username


@register(User)
class UserAdmin(PonyORMModelAdmin):
    exclude = ("hash_password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    @db_session
    def authenticate(self, username, password):
        user = next((f for f in self.model_cls.select(username=username, password=password, is_superuser=True)), None)
        if not user:
            return None
        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return None
        return user.id
