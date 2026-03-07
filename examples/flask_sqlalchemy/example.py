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

from fastadmin import (
    SqlAlchemyInlineModelAdmin,
    SqlAlchemyModelAdmin,
    WidgetActionArgumentProps,
    WidgetActionChartProps,
    WidgetActionFilter,
    WidgetActionInputSchema,
    WidgetActionParentArgumentProps,
    WidgetActionProps,
    WidgetActionResponseSchema,
    WidgetActionType,
    WidgetType,
    action,
    display,
)
from fastadmin import flask_app as admin_app
from fastadmin import (
    register,
    widget_action,
)
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
    widget_actions = (
        "sales_chart",
        "sales_area_chart",
        "sales_column_chart",
        "sales_bar_chart",
        "sales_pie_chart",
        "sales_action",
    )

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

    async def pre_generate_models_schema(self) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            result = await session.execute(select(self.model_cls.username))
            options = list(result.scalars().all())
        widget_action_props: WidgetActionProps = self.__class__.sales_action.widget_action_props
        for argument in widget_action_props.arguments:
            if argument.name == "username":
                argument.widget_props["options"] = [{"label": option, "value": option} for option in options]
                break

    @widget_action(
        widget_action_type=WidgetActionType.ChartLine,
        widget_action_props=WidgetActionChartProps(
            x_field="x",
            y_field="y",
            series_field="series",
            series_color={
                "Sales": "#1677ff",
                "Sales 2": "#52c41a",
            },
        ),
        widget_action_filters=[
            WidgetActionFilter(
                field_name="x",
                widget_type=WidgetType.DatePicker,
            ),
            WidgetActionFilter(
                field_name="y",
                widget_type=WidgetType.Select,
                widget_props={
                    "options": [
                        {"label": "Sales", "value": "sales"},
                        {"label": "Revenue", "value": "revenue"},
                    ],
                },
            ),
        ],
        tab="Analytics",
        title="Sales over time",
        description="Line chart of sales",
        width=24,
    )
    async def sales_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {"x": "2026-01-01", "y": 100, "series": "Sales"},
                {"x": "2026-01-02", "y": 200, "series": "Sales"},
                {"x": "2026-01-01", "y": 300, "series": "Sales 2"},
                {"x": "2026-01-04", "y": 400, "series": "Sales 2"},
            ],
        )

    @widget_action(
        widget_action_type=WidgetActionType.ChartArea,
        widget_action_props=WidgetActionChartProps(
            x_field="x",
            y_field="y",
            series_field="series",
            series_color={
                "Online": "#722ed1",
                "Retail": "#13c2c2",
            },
        ),
        widget_action_filters=[
            WidgetActionFilter(
                field_name="period",
                widget_type=WidgetType.RangePicker,
            ),
            WidgetActionFilter(
                field_name="channel",
                widget_type=WidgetType.Select,
                widget_props={
                    "mode": "multiple",
                    "options": [
                        {"label": "Online", "value": "Online"},
                        {"label": "Retail", "value": "Retail"},
                    ],
                },
            ),
        ],
        tab="Analytics",
        title="Sales trend area",
        description="Area chart of sales",
        width=12,
    )
    async def sales_area_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {"x": "2026-01-01", "y": 80, "series": "Online"},
                {"x": "2026-01-02", "y": 120, "series": "Online"},
                {"x": "2026-01-01", "y": 60, "series": "Retail"},
                {"x": "2026-01-02", "y": 90, "series": "Retail"},
            ],
        )

    @widget_action(
        widget_action_type=WidgetActionType.ChartColumn,
        widget_action_props=WidgetActionChartProps(
            x_field="x",
            y_field="y",
            series_field="series",
            series_color={
                "2025": "#fa8c16",
                "2026": "#f5222d",
            },
        ),
        widget_action_filters=[
            WidgetActionFilter(
                field_name="year",
                widget_type=WidgetType.Select,
                widget_props={
                    "options": [
                        {"label": "2025", "value": "2025"},
                        {"label": "2026", "value": "2026"},
                    ],
                },
            ),
        ],
        tab="Analytics",
        title="Sales by month",
        description="Column chart of sales",
        width=12,
    )
    async def sales_column_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {"x": "Jan", "y": 320, "series": "2025"},
                {"x": "Feb", "y": 410, "series": "2025"},
                {"x": "Jan", "y": 380, "series": "2026"},
                {"x": "Feb", "y": 460, "series": "2026"},
            ],
        )

    @widget_action(
        widget_action_type=WidgetActionType.ChartBar,
        widget_action_props=WidgetActionChartProps(
            x_field="x",
            y_field="y",
            series_field="series",
            series_color={
                "Q1": "#2f54eb",
                "Q2": "#eb2f96",
            },
        ),
        widget_action_filters=[
            WidgetActionFilter(
                field_name="quarter",
                widget_type=WidgetType.Select,
                widget_props={
                    "options": [
                        {"label": "Q1", "value": "Q1"},
                        {"label": "Q2", "value": "Q2"},
                    ],
                },
            ),
        ],
        tab="Analytics",
        title="Sales by region",
        description="Bar chart of sales",
        width=12,
    )
    async def sales_bar_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {"x": "North", "y": 540, "series": "Q1"},
                {"x": "South", "y": 420, "series": "Q1"},
                {"x": "North", "y": 610, "series": "Q2"},
                {"x": "South", "y": 480, "series": "Q2"},
            ],
        )

    @widget_action(
        widget_action_type=WidgetActionType.ChartPie,
        widget_action_props=WidgetActionChartProps(
            x_field="x",
            y_field="y",
            series_color=[
                "#1677ff",
                "#52c41a",
                "#faad14",
            ],
        ),
        widget_action_filters=[
            WidgetActionFilter(
                field_name="month",
                widget_type=WidgetType.DatePicker,
            ),
        ],
        tab="Analytics",
        title="Sales share",
        description="Pie chart of sales share",
        width=12,
    )
    async def sales_pie_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {"x": "Online", "y": 45},
                {"x": "Retail", "y": 30},
                {"x": "Partners", "y": 25},
            ],
        )

    @widget_action(
        widget_action_type=WidgetActionType.Action,
        widget_action_props=WidgetActionProps(
            arguments=[
                # Example of using AsyncSelect widget with parentModel
                WidgetActionArgumentProps(
                    name="user_id",
                    widget_type=WidgetType.AsyncSelect,
                    widget_props={
                        "required": True,
                        "parentModel": "User",
                        "idField": "id",
                        "labelFields": ["__str__", "id"],
                    },
                ),
                # Example of using Select widget with dynamically loaded options
                WidgetActionArgumentProps(
                    name="username",
                    widget_type=WidgetType.Select,
                    widget_props={
                        "required": True,
                        # dynamically load options from the database in pre_generate_models_schema method
                        "options": [],
                    },
                ),
                # Example of using parent argument with filtered children arguments
                WidgetActionArgumentProps(
                    name="type",
                    widget_type=WidgetType.Select,
                    widget_props={
                        "required": True,
                        "options": [
                            {"label": "Sales", "value": "sales"},
                            {"label": "Revenue", "value": "revenue"},
                        ],
                    },
                ),
                WidgetActionArgumentProps(
                    name="sales_date",
                    widget_type=WidgetType.DatePicker,
                    widget_props={
                        "required": True,
                    },
                    parent_argument=WidgetActionParentArgumentProps(
                        name="type",
                        value="sales",
                    ),
                ),
                WidgetActionArgumentProps(
                    name="revenue_date",
                    widget_type=WidgetType.DatePicker,
                    widget_props={
                        "required": True,
                    },
                    parent_argument=WidgetActionParentArgumentProps(
                        name="type",
                        value="revenue",
                    ),
                ),
            ],
        ),
        tab="Data",
        title="Get sales data",
        description="Get sales data",
        width=12,
    )
    async def sales_action(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {"id": 1, "name": "Sales"},
                {"id": 2, "name": "Sales"},
                {"id": 3, "name": "Sales"},
            ],
        )


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
