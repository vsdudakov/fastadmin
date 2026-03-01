import asyncio
import os
import uuid

os.environ["ADMIN_USER_MODEL"] = "User"
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = "username"
os.environ["ADMIN_SECRET_KEY"] = "secret"

from flask import Flask
from flask_cors import CORS
from models import Base, BaseEvent, Event, Tournament, User, sqlalchemy_engine, sqlalchemy_sessionmaker
from sqlalchemy import select, update

from fastadmin import SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin, WidgetType, action, display
from fastadmin import flask_app as admin_app
from fastadmin import register
from fastadmin.api.frameworks.flask.app import JSONProvider
from fastadmin.settings import settings


@register(User, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class UserModelAdmin(SqlAlchemyModelAdmin):
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
            },
        ),
        "attachment_url": (
            WidgetType.UploadFile,
            {
                "required": True,
            },
        ),
    }

    async def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = select(self.model_cls).filter_by(username=username, password=password, is_superuser=True)
            result = await session.scalars(query)
            obj = result.first()
            if not obj:
                return None
            return obj.id

    async def change_password(self, id: uuid.UUID | int, password: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = update(self.model_cls).where(User.id.in_([id])).values(password=password)
            await session.execute(query)
            await session.commit()

    async def upload_file(
        self,
        field_name: str,
        file_name: str,
        file_content: bytes,
    ) -> str:
        # save file to media directory or to s3/filestorage here
        return f"/media/{file_name}"


class EventInlineModelAdmin(SqlAlchemyInlineModelAdmin):
    model = Event


@register(Tournament, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class TournamentModelAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class BaseEventModelAdmin(SqlAlchemyModelAdmin):
    pass


@register(Event, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class EventModelAdmin(SqlAlchemyModelAdmin):
    actions = ("make_is_active", "make_is_not_active")
    list_display = ("id", "tournament", "name_with_price", "rating", "event_type", "is_active", "started")
    list_filter = ("tournament", "event_type", "is_active")
    search_fields = ("name", "tournament__name")

    @action(description="Make event active")
    async def make_is_active(self, ids):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = update(Event).where(Event.id.in_(ids)).values(is_active=True)
            await session.execute(query)
            await session.commit()

    @action
    async def make_is_not_active(self, ids):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = update(Event).where(Event.id.in_(ids)).values(is_active=False)
            await session.execute(query)
            await session.commit()

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"


async def init_db():
    async with sqlalchemy_engine.begin() as c:
        await c.run_sync(Base.metadata.drop_all)
        await c.run_sync(Base.metadata.create_all)


async def create_superuser():
    async with sqlalchemy_sessionmaker() as s:
        user = User(
            username="admin",
            password="admin",
            is_superuser=True,
            attachment_url="/media/attachment.txt",
        )
        s.add(user)
        await s.commit()


def run_async_init():
    asyncio.run(init_db())
    asyncio.run(create_superuser())


app = Flask(__name__)
app.json = JSONProvider(app)
app.register_blueprint(admin_app, url_prefix=f"/{settings.ADMIN_PREFIX}")

CORS(
    app,
    origins=["http://localhost:3030", "http://localhost:8090"],
    supports_credentials=True,
)

if __name__ == "__main__":
    run_async_init()
    app.run(host="0.0.0.0", port=8090, debug=True)  # noqa: S201
