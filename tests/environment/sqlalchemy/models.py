import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Time,
    select,
    update,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from fastadmin import SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin, action, display, register


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    @classmethod
    def get_model_name(cls):
        return f"sqlalchemy.{cls.__name__}"


user_m2m_event = Table(
    "event_participants",
    Base.metadata,
    Column("event_id", ForeignKey("event.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True),
)


class User(BaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(length=255), nullable=False)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    events: Mapped[list["Event"]] = relationship(secondary=user_m2m_event, back_populates="participants")

    async def __str__(self):
        return self.username


class Tournament(BaseModel):
    __tablename__ = "tournament"

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    events: Mapped[list["Event"]] = relationship(back_populates="tournament")

    async def __str__(self):
        return self.name


class BaseEvent(BaseModel):
    __tablename__ = "base_event"

    event: Mapped[Optional["Event"]] = relationship(back_populates="base")


class Event(BaseModel):
    __tablename__ = "event"

    base_id: Mapped[int | None] = mapped_column(ForeignKey("base_event.id"), nullable=True)
    base: Mapped[Optional["BaseEvent"]] = relationship(back_populates="event")

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    tournament_id: Mapped[int | None] = mapped_column(ForeignKey("tournament.id"), nullable=False)
    tournament: Mapped[Optional["Tournament"]] = relationship(back_populates="events")

    participants: Mapped[list["User"]] = relationship(secondary=user_m2m_event, back_populates="events")

    rating: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=False)
    event_type: Mapped[EventTypeEnum] = mapped_column(default=EventTypeEnum.PUBLIC)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_time: Mapped[datetime.time | None] = mapped_column(Time, nullable=True)
    date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    price: Mapped[Decimal | None] = mapped_column(
        Float(asdecimal=True), nullable=True
    )  # max_digits=10, decimal_places=2

    json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    async def __str__(self):
        return self.name


# NOTE: provide sqlalchemy_sessionmaker as second parameter for your usage
# @register(User, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
@register(User)
class SqlAlchemyUserModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"

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
            # direct saving password is only for tests - use hash
            query = update(self.model_cls).where(User.id.in_([user_id])).values(password=password)
            await session.execute(query)
            await session.commit()


class SqlAlchemyEventInlineModelAdmin(SqlAlchemyInlineModelAdmin):
    model_name_prefix = "sqlalchemy"

    model = Event


# NOTE: provide sqlalchemy_sessionmaker as second parameter for your usage
# @register(Tournament, sqlalchemy_sessionmaker)
@register(Tournament)
class SqlAlchemyTournamentModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"

    inlines = (SqlAlchemyEventInlineModelAdmin,)


# NOTE: provide sqlalchemy_sessionmaker as second parameter for your usage
# @register(BaseEvent, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
@register(BaseEvent)
class SqlAlchemyBaseEventModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"


# NOTE: provide sqlalchemy_sessionmaker as second parameter for your usage
# @register(Event, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
@register(Event)
class SqlAlchemyEventModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"

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
