import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

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
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from fastadmin import SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin, action, display, register
from tests.settings import DB_SQLITE

sqlalchemy_engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_SQLITE}",
    echo=True,
)
sqlalchemy_sessionmaker = async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


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

    events: Mapped[List["Event"]] = relationship(secondary=user_m2m_event, back_populates="participants")


class Tournament(BaseModel):
    __tablename__ = "tournament"

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    events: Mapped[List["Event"]] = relationship(back_populates="tournament")


class BaseEvent(BaseModel):
    __tablename__ = "base_event"

    event: Mapped[Optional["Event"]] = relationship(back_populates="base")


class Event(BaseModel):
    __tablename__ = "event"

    base_id: Mapped[Optional[int]] = mapped_column(ForeignKey("base_event.id"), nullable=True)
    base: Mapped[Optional["BaseEvent"]] = relationship(back_populates="event")

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    tournament_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tournament.id"), nullable=False)
    tournament: Mapped[Optional["Tournament"]] = relationship(back_populates="events")

    participants: Mapped[list["User"]] = relationship(secondary=user_m2m_event, back_populates="events")

    rating: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=False)
    event_type: Mapped[EventTypeEnum] = mapped_column(default=EventTypeEnum.PUBLIC)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_time: Mapped[Optional[datetime.time]] = mapped_column(Time, nullable=True)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price: Mapped[Optional[Decimal]] = mapped_column(
        Float(asdecimal=True), nullable=True
    )  # max_digits=10, decimal_places=2

    json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


@register(User)
class SqlAlchemyUserModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"
    sqlalchemy_sessionmaker = sqlalchemy_sessionmaker

    async def authenticate(self, username, password):
        async with self.sqlalchemy_sessionmaker() as session:
            query = select(User).filter_by(username=username, password=password, is_superuser=True)
            result = await session.scalars(query)
            obj = result.first()
            if not obj:
                return None
            return obj.id


class SqlAlchemyEventInlineModelAdmin(SqlAlchemyInlineModelAdmin):
    model_name_prefix = "sqlalchemy"
    sqlalchemy_sessionmaker = sqlalchemy_sessionmaker

    model = Event
    fk_name = "tournament"


@register(Tournament)
class SqlAlchemyTournamentModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"
    sqlalchemy_sessionmaker = sqlalchemy_sessionmaker

    inlines = (SqlAlchemyEventInlineModelAdmin,)


@register(Event)
class SqlAlchemyEventModelAdmin(SqlAlchemyModelAdmin):
    model_name_prefix = "sqlalchemy"
    sqlalchemy_sessionmaker = sqlalchemy_sessionmaker

    @action(description="Make user active")
    async def make_is_active(self, ids):
        async with self.sqlalchemy_sessionmaker() as session:
            query = update(Event).where(Event.id.in_(ids)).values(is_active=True)
            await session.execute(query)
            await session.commit()

    @action
    async def make_is_not_active(self, ids):
        async with self.sqlalchemy_sessionmaker() as session:
            query = update(Event).where(Event.id.in_(ids)).values(is_active=False)
            await session.execute(query)
            await session.commit()

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"
