from typing import List

from fastapi import FastAPI
from sqlalchemy import Boolean, Integer, String, select, ForeignKey
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from fastadmin import SqlAlchemyModelAdmin, register, fastapi_app as admin_app


sqlalchemy_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
sqlalchemy_sessionmaker = async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(String(length=255), nullable=False)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user")

    def __str__(self):
        return self.username


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(back_populates="transactions")


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
            is_active=True,
        )
        s.add(user)
        await s.commit()


@register(User, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class UserAdmin(SqlAlchemyModelAdmin):
    exclude = ("password",)
    list_display = ("id", "username", "is_superuser", "is_active")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active")
    search_fields = ("username",)

    async def authenticate(self, username, password):
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = select(User).filter_by(
                username=username, password=password, is_superuser=True
            )
            result = await session.scalars(query)
            user = result.first()
            if not user:
                return None
            if password != user.password:
                return None
            return user.id

@register(Transaction, sqlalchemy_sessionmaker=sqlalchemy_sessionmaker)
class TransactionAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "user")
    raw_id_fields = ("user",)


app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_db()
    await create_superuser()


app.mount("/admin", admin_app)
