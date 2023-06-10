from datetime import datetime, timedelta, timezone
from typing import Any

from django.db import connection, models

from fastadmin import DashboardWidgetAdmin, DashboardWidgetType, WidgetType, register_widget


class DashboardUser(models.Model):
    username = models.CharField(max_length=255, unique=True)
    hash_password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.username


@register_widget
class UsersDashboardWidgetAdmin(DashboardWidgetAdmin):
    title = "Users"
    dashboard_widget_type = DashboardWidgetType.ChartLine
    x_field = "date"
    y_field = "count"
    x_field_filter_widget_type = WidgetType.DatePicker
    x_field_filter_widget_props = {"picker": "month"}
    x_field_periods = ["day", "week", "month", "year"]

    def get_data(  # type: ignore [override]
        self,
        min_x_field: str | None = None,
        max_x_field: str | None = None,
        period_x_field: str | None = None,
    ) -> dict[str, Any]:
        def dictfetchall(cursor):
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]

        with connection.cursor() as c:
            if not min_x_field:
                min_x_field_date = datetime.now(timezone.utc) - timedelta(days=360)
            else:
                min_x_field_date = datetime.fromisoformat(min_x_field.replace("Z", "+00:00"))
            if not max_x_field:
                max_x_field_date = datetime.now(timezone.utc) + timedelta(days=1)
            else:
                max_x_field_date = datetime.fromisoformat(max_x_field.replace("Z", "+00:00"))

            if not period_x_field or period_x_field not in self.x_field_periods:
                period_x_field = "month"

            c.execute(
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
            results = dictfetchall(c)
            return {
                "results": results,
                "min_x_field": min_x_field_date.isoformat().replace("+00:00", "Z"),
                "max_x_field": max_x_field_date.isoformat().replace("+00:00", "Z"),
                "period_x_field": period_x_field,
            }
