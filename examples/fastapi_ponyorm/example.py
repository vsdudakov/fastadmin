import asyncio
import os
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

os.environ["ADMIN_USER_MODEL"] = "User"
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = "username"
os.environ["ADMIN_SECRET_KEY"] = "secret"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import BaseEvent, Event, Tournament, User, db
from pony.orm import commit, db_session
from pony.orm import select as pony_select

from fastadmin import (
    PonyORMInlineModelAdmin,
    PonyORMModelAdmin,
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
from fastadmin import fastapi_app as admin_app
from fastadmin import (
    register,
    widget_action,
)


@register(User)
class UserModelAdmin(PonyORMModelAdmin):
    menu_section = "Users"
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
                # Disable crop image for upload field
                # "disableCropImage": True,
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

    @db_session
    def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        obj = next((f for f in User.select(username=username, password=password, is_superuser=True)), None)  # fmt: skip
        if not obj:
            return None
        return obj.id

    @db_session
    def change_password(self, id: uuid.UUID | int, password: str) -> None:
        obj = next((f for f in self.model_cls.select(id=id)), None)
        if not obj:
            return
        # direct saving password is only for tests - use hash
        obj.password = password
        commit()

    def upload_file(
        self,
        field_name: str,
        file_name: str,
        file_content: bytes,
    ) -> str:
        """This method is used to upload files.

        :params field_name: a name of field.
        :params file_name: a name of file.
        :params file_content: a content of file.
        :return: A file url.
        """
        # save file to media directory or to s3/filestorage here
        # return a full url to the file
        return f"https://fastadmin.io/media/{file_name}"

    async def pre_generate_models_schema(self) -> None:
        def get_options() -> list:
            with db_session:
                return [u.username for u in pony_select(u for u in User)]

        options = await asyncio.to_thread(get_options)
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
        sub_tab="Sales",
        title="Sales over time",
        description="Line chart of sales",
        width=24,
    )
    def sales_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
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
    def sales_area_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
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
    def sales_column_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
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
    def sales_bar_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
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
    def sales_pie_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
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
    def sales_action(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        return WidgetActionResponseSchema(
            data=[
                {"id": 1, "name": "Sales"},
                {"id": 2, "name": "Sales"},
                {"id": 3, "name": "Sales"},
            ],
        )


class EventInlineModelAdmin(PonyORMInlineModelAdmin):
    model = Event


@register(Tournament)
class TournamentModelAdmin(PonyORMModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent)
class BaseEventModelAdmin(PonyORMModelAdmin):
    pass


@register(Event)
class EventModelAdmin(PonyORMModelAdmin):
    actions = ("make_is_active", "make_is_not_active")
    list_display = ("id", "tournament", "name_with_price", "rating", "event_type", "is_active", "started")
    list_filter = ("tournament", "event_type", "is_active")
    search_fields = ("name", "tournament__name")

    @action(description="Make event active")
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
    @db_session
    def started(self, obj):
        return bool(obj.start_time)

    @display()
    @db_session
    def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"


def init_db():
    # Use shared in-memory sqlite DB so tables are visible across connections/threads.
    db.bind(provider="sqlite", filename=":sharedmemory:", create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def create_superuser():
    User(
        username="admin",
        password="admin",
        is_superuser=True,
        attachment_url="/media/attachment.txt",
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    create_superuser()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/admin", admin_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3030", "http://localhost:8090"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
