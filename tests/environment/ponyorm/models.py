from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum

from pony.orm import Database, Json, LongStr, Optional, PrimaryKey, Required, Set, commit, db_session
from pony.orm.dbapiprovider import StrConverter

from fastadmin import PonyORMInlineModelAdmin, PonyORMModelAdmin, action, display, register

db = Database()


class EnumConverter(StrConverter):
    def validate(self, val):
        if not isinstance(val, Enum):
            raise ValueError(f"Must be an Enum. Got {type(val)}")
        return val

    def py2sql(self, val):
        return val.name

    def sql2py(self, value):
        return self.py_type[value]


class EventTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class BaseModel:
    @classmethod
    def get_model_name(cls):
        return f"ponyorm.{cls.__name__}"


class User(BaseModel, db.Entity):  # type: ignore [name-defined]
    _table_ = "user"

    id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow, hidden=True)
    updated_at = Required(datetime, default=datetime.utcnow, hidden=True)

    username = Required(str)
    password = Required(str)
    is_superuser = Required(bool, default=False)

    events = Set("Event", table="event_participants", column="event_id")

    def __str__(self):
        return self.username


class Tournament(BaseModel, db.Entity):   # type: ignore [name-defined]
    _table_ = "tournament"

    id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow, hidden=True)
    updated_at = Required(datetime, default=datetime.utcnow, hidden=True)

    name = Required(str)

    events = Set("Event")

    def __str__(self):
        return self.name


class BaseEvent(BaseModel, db.Entity):  # type: ignore [name-defined]
    _table_ = "base_event"
    id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow, hidden=True)
    updated_at = Required(datetime, default=datetime.utcnow, hidden=True)

    event = Optional("Event")


class Event(BaseModel, db.Entity):  # type: ignore [name-defined]
    _table_ = "event"

    id = PrimaryKey(int, auto=True)
    created_at = Required(datetime, default=datetime.utcnow, hidden=True)
    updated_at = Required(datetime, default=datetime.utcnow, hidden=True)

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


@register(User)
class PonyORMUserModelAdmin(PonyORMModelAdmin):
    model_name_prefix = "ponyorm"

    @db_session
    def authenticate(self, username, password):
        obj = next((f for f in self.model_cls.select(username=username, password=password, is_superuser=True)), None)
        if not obj:
            return None
        return obj.id

    @db_session
    def change_password(self, user_id, password):
        obj = next((f for f in self.model_cls.select(id=user_id)), None)
        if not obj:
            return
        # direct saving password is only for tests - use hash
        obj.password = password
        commit()


class PonyORMEventInlineModelAdmin(PonyORMInlineModelAdmin):
    model = Event
    model_name_prefix = "ponyorm"


@register(Tournament)
class PonyORMTournamentModelAdmin(PonyORMModelAdmin):
    inlines = (PonyORMEventInlineModelAdmin,)
    model_name_prefix = "ponyorm"


@register(BaseEvent)
class PonyORMBaseEventModelAdmin(PonyORMModelAdmin):
    model_name_prefix = "ponyorm"


@register(Event)
class PonyORMEventModelAdmin(PonyORMModelAdmin):
    model_name_prefix = "ponyorm"

    @action(description="Make user active")
    @db_session
    def make_is_active(self, ids):
        # update(o.set(is_active=True) for o in self.model_cls if o.id in ids)
        objs = self.model_cls.select(lambda o: o.id in ids)
        for obj in objs:
            obj.is_active = True
        commit()

    @action
    @db_session
    def make_is_not_active(self, ids):
        # update(o.set(is_active=False) for o in self.model_cls if o.id in ids)
        objs = self.model_cls.select(lambda o: o.id in ids)
        for obj in objs:
            obj.is_active = False
        commit()

    @display
    async def started(self, obj):
        return bool(obj.start_time)

    @display()
    async def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"
