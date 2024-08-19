from datetime import UTC, date, datetime, time
from decimal import Decimal
from enum import Enum

from pony.orm import Database, Json, LongStr, Optional, PrimaryKey, Required, Set

db = Database()


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel:
    # id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Required(datetime, default=datetime.utcnow)

    def before_update(self):
        self.updated_at = datetime.now(tz=UTC)

    @classmethod
    def get_model_name(cls):
        return f"ponyorm.{cls.__name__}"


class User(db.Entity, BaseModel):
    _table_ = "user"

    username = Required(str, max_len=255)
    password = Required(str, max_len=255)
    is_superuser = Required(bool, default=False)

    events = Set("Event", table="event_participants", column="event_id")

    def __str__(self):
        return self.username


class Tournament(db.Entity, BaseModel):
    _table_ = "tournament"

    name = Required(str, max_len=255)

    events = Set("Event")

    def __str__(self):
        return self.name


class BaseEvent(db.Entity, BaseModel):
    _table_ = "base_event"

    id = PrimaryKey(int, auto=True)
    name = Required(str, max_len=255)

    event = Optional("Event")

    def __str__(self):
        return self.name


class Event(db.Entity, BaseModel):
    _table_ = "event"

    base = Optional(BaseEvent, column="base_id")
    name = Required(str)

    tournament = Required(Tournament, column="tournament_id")
    participants = Set(User, table="event_participants", column="user_id")

    rating = Required(int, default=0)
    description = Optional(LongStr)
    event_type = Required(EventTypeEnum, default=EventTypeEnum.PUBLIC)
    is_active = Required(bool, default=True)
    start_time = Optional(time)
    date = Optional(date)
    latitude = Optional(float)
    longitude = Optional(float)
    price = Optional(Decimal)

    json = Optional(Json)

    def __str__(self):
        return self.name
