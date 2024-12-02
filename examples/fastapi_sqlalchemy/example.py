from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Base, BaseEvent, Event, Tournament, User, sqlalchemy_engine, sqlalchemy_sessionmaker
from sqlalchemy import select, update

from fastadmin import SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin, WidgetType, action, display
from fastadmin import fastapi_app as admin_app
from fastadmin import register


@register(User, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class UserModelAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
        "avatar_url": (WidgetType.Upload, {"required": False}),
    }

    async def authenticate(self, username, password):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = select(self.model_cls).filter_by(username=username, password=password, is_superuser=True)
            result = await session.scalars(query)
            obj = result.first()
            if not obj:
                return None
            return obj.id

    async def change_password(self, user_id, password):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            # use hash password for real usage
            query = update(self.model_cls).where(User.id.in_([user_id])).values(password=password)
            await session.execute(query)
            await session.commit()


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
    list_display = ("id", "name_with_price", "rating", "event_type", "is_active", "started")

    @action(description="Make user active")
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


app = FastAPI()


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
        )
        s.add(user)
        await s.commit()


@app.on_event("startup")
async def startup():
    await init_db()
    await create_superuser()


app.mount("/admin", admin_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
