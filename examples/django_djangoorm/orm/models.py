import asyncio
import uuid

from django.db import models

from fastadmin import (
    DjangoInlineModelAdmin,
    DjangoModelAdmin,
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
    register,
    widget_action,
)

EventTypeEnum = (
    ("PRIVATE", "PRIVATE"),
    ("PUBLIC", "PUBLIC"),
)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)

    avatar_url = models.ImageField(null=True)
    attachment_url = models.FileField()

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"


class Tournament(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tournament"


class BaseEvent(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "base_event"


class Event(BaseModel):
    base = models.OneToOneField(BaseEvent, related_name="event", null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)

    tournament = models.ForeignKey(Tournament, related_name="events", on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name="events")

    rating = models.IntegerField(default=0)
    description = models.TextField(null=True)
    event_type = models.CharField(max_length=255, default="PUBLIC", choices=EventTypeEnum)
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField(null=True)
    date = models.DateField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    json = models.JSONField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "event"


@register(User)
class UserModelAdmin(DjangoModelAdmin):
    menu_section = "Users"
    list_display = ("id", "username", "is_superuser")
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser")
    search_fields = ("username",)
    formfield_overrides = {  # noqa: RUF012
        "username": (WidgetType.SlugInput, {"required": True}),
        "password": (WidgetType.PasswordInput, {"passwordModalForm": True}),
    }
    widget_actions = (
        "sales_chart",
        "sales_area_chart",
        "sales_column_chart",
        "sales_bar_chart",
        "sales_pie_chart",
        "sales_action",
    )

    def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        obj = self.model_cls.objects.filter(username=username, is_superuser=True).first()
        if not obj:
            return None
        # if not obj.check_password(password):
        #     return None
        return obj.id

    def change_password(self, id: uuid.UUID | int, password: str) -> None:
        user = self.model_cls.objects.filter(id=id).first()
        if not user:
            return
        # direct saving password is only for tests - use hash
        user.password = password
        user.save()

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
            return list(self.model_cls.objects.values_list("username", flat=True))

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


class EventInlineModelAdmin(DjangoInlineModelAdmin):
    model = Event


@register(Tournament)
class TournamentModelAdmin(DjangoModelAdmin):
    list_display = ("id", "name")
    inlines = (EventInlineModelAdmin,)


@register(BaseEvent)
class BaseEventModelAdmin(DjangoModelAdmin):
    pass


@register(Event)
class EventModelAdmin(DjangoModelAdmin):
    actions = ("make_is_active", "make_is_not_active")
    list_display = ("id", "tournament", "name_with_price", "rating", "event_type", "is_active", "started")
    list_filter = ("tournament", "event_type", "is_active")
    search_fields = ("name", "tournament__name")

    @action(description="Make event active")
    def make_is_active(self, ids):
        self.model_cls.objects.filter(id__in=ids).update(is_active=True)

    @action
    def make_is_not_active(self, ids):
        self.model_cls.objects.filter(id__in=ids).update(is_active=False)

    @display
    def started(self, obj):
        return bool(obj.start_time)

    @display()
    def name_with_price(self, obj):
        return f"{obj.name} - {obj.price}"
