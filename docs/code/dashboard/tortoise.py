import datetime

from tortoise import Tortoise, fields
from tortoise.models import Model

from fastadmin import DashboardWidgetAdmin, DashboardWidgetType, WidgetType, register_widget


class DashboardUser(Model):
    username = fields.CharField(max_length=255, unique=True)
    hash_password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=False)

    def __str__(self):
        return self.username


@register_widget
class UsersDashboardWidgetAdmin(DashboardWidgetAdmin):
    title = "Users"
    dashboard_widget_type = DashboardWidgetType.ChartLine

    x_field = "date"
    x_field_filter_widget_type = WidgetType.DatePicker
    x_field_filter_widget_props: dict[str, str] = {"picker": "month"}  # noqa: RUF012
    x_field_periods = ["day", "week", "month", "year"]  # noqa: RUF012

    y_field = "count"

    async def get_data(
        self,
        min_x_field: str | None = None,
        max_x_field: str | None = None,
        period_x_field: str | None = None,
    ) -> dict:
        conn = Tortoise.get_connection("default")

        if not min_x_field:
            min_x_field_date = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=360)
        else:
            min_x_field_date = datetime.datetime.fromisoformat(min_x_field)
        if not max_x_field:
            max_x_field_date = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
        else:
            max_x_field_date = datetime.datetime.fromisoformat(max_x_field)

        if not period_x_field or period_x_field not in (self.x_field_periods or []):
            period_x_field = "month"

        results = await conn.execute_query_dict(
            """
                SELECT
                    to_char(date_trunc($1, "user"."created_at")::date, 'dd/mm/yyyy') "date",
                    COUNT("user"."id") "count"
                FROM "user"
                WHERE "user"."created_at" >= $2 AND "user"."created_at" <= $3
                GROUP BY "date" ORDER BY "date"
            """,
            [period_x_field, min_x_field_date, max_x_field_date],
        )
        return {
            "results": results,
            "min_x_field": min_x_field_date.isoformat(),
            "max_x_field": max_x_field_date.isoformat(),
            "period_x_field": period_x_field,
        }
