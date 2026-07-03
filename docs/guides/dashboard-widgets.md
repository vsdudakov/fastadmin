---
title: Dashboard widgets
description: Add chart and action widgets to the FastAdmin dashboard with the widget_action decorator.
---

# Dashboard widgets

Dashboard widgets are declared with the `@widget_action` decorator on model
admin methods, and enabled by listing the method names in the admin's
`widget_actions` attribute.

!!! warning

    If you forget to add the method name to `widget_actions`, the widget will
    not appear on the dashboard.

```python
from fastadmin import TortoiseModelAdmin, register, widget_action
from fastadmin import (
    WidgetActionChartProps,
    WidgetActionInputSchema,
    WidgetActionResponseSchema,
    WidgetActionType,
)


@register(User)
class UserAdmin(TortoiseModelAdmin):
    # Register widgets by method name
    widget_actions = ("users_chart",)

    @widget_action(
        widget_action_type=WidgetActionType.ChartLine,
        widget_action_props=WidgetActionChartProps(x_field="x", y_field="y"),
        tab="Analytics",
        title="Users over time",
    )
    async def users_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        # Build and return data for the chart
        return WidgetActionResponseSchema(
            data=[
                {"x": "2026-01-01", "y": 10},
                {"x": "2026-01-02", "y": 15},
            ],
        )
```

## Widget action types

`WidgetActionType` selects how the result is rendered:

| Type | Renders |
| --- | --- |
| `ChartLine` | Line chart |
| `ChartArea` | Area chart |
| `ChartColumn` | Column chart |
| `ChartBar` | Bar chart |
| `ChartPie` | Pie chart |
| `Action` | A plain action widget (button + result view with table/JSON output, search highlighting, copy-to-clipboard and expand modal) |

Charts are rendered with
[antd charts](https://ant-design-charts.antgroup.com/en/examples) — see their
gallery for how each type looks.

## Decorator parameters

```python
@widget_action(
    tab="Default",              # dashboard tab the widget appears on
    sub_tab=None,               # optional sub-tab within the tab
    title="Action",             # widget title
    description=None,           # short description
    widget_action_type=WidgetActionType.Action,
    widget_action_props=None,   # WidgetActionChartProps or WidgetActionProps
    widget_action_filters=None, # list[WidgetActionFilter]
    width=None,                 # width in the 1-24 grid system
    max_height=None,            # max height in px
)
```

Calling `@widget_action()` without arguments uses the defaults above.

## Chart props, arguments and filters

- **`WidgetActionChartProps(x_field, y_field, series_field=None,
  series_color=None)`** — maps the returned data rows onto chart axes; use
  `series_field` for multi-series charts and `series_color` (list or dict) to
  pin colors.
- **`WidgetActionProps(arguments=[WidgetActionArgumentProps(...)])`** — for
  `Action` widgets: renders an input form. Each argument has a `name`, a
  `widget_type` ([any form widget](form-widgets.md#widget-types)),
  optional `widget_props`, and an optional
  `parent_argument=WidgetActionParentArgumentProps(name=..., value=...)` to
  show it only when another argument has a given value.
- **`WidgetActionFilter(field_name, widget_type, widget_props=None)`** —
  renders filter controls above the widget; selected values arrive in the
  payload.

The handler receives a `WidgetActionInputSchema` whose `query` is a list of
`WidgetActionQuerySchema(field_name, widget_type, value)` — one entry per
filter/argument the user set — and returns a `WidgetActionResponseSchema`
with a list of data rows:

```python
from fastadmin import (
    WidgetActionChartProps,
    WidgetActionFilter,
    WidgetActionInputSchema,
    WidgetActionResponseSchema,
    WidgetActionType,
    WidgetType,
    widget_action,
)


@widget_action(
    tab="Sales",
    title="Total sales by status",
    widget_action_type=WidgetActionType.ChartColumn,
    widget_action_props=WidgetActionChartProps(
        x_field="date",
        y_field="total_sales",
        series_field="status",
    ),
    widget_action_filters=[
        WidgetActionFilter(
            field_name="status",
            widget_type=WidgetType.Select,
            widget_props={
                "mode": "multiple",
                "options": [
                    {"label": "Pending", "value": "Pending"},
                    {"label": "Completed", "value": "Completed"},
                ],
            },
        )
    ],
)
async def sales_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
    statuses = [q.value for q in payload.query if q.field_name == "status"]
    # ...query your ORM using the selected statuses...
    return WidgetActionResponseSchema(
        data=[
            {"date": "2026-01-01", "total_sales": 100, "status": "Pending"},
            {"date": "2026-01-02", "total_sales": 200, "status": "Completed"},
        ],
    )
```

Complete widget examples for every ORM are in
[Registering models](registering-models.md#complete-examples).
