"""Tests for dashboard widget API (covers exception paths in FastAPI/Flask/Django)."""


async def test_dashboard_widget_401(client):
    """Dashboard widget returns 401 when not authenticated."""
    r = await client.get("/api/dashboard-widget/SomeWidget")
    assert r.status_code == 401


async def test_dashboard_widget_404(session_id, client):
    """Dashboard widget returns 404 when widget model is not registered."""
    assert session_id
    r = await client.get("/api/dashboard-widget/NonExistentWidget")
    assert r.status_code == 404


async def test_dashboard_widget_200(session_id, client):
    """Dashboard widget returns data for a registered widget."""
    assert session_id
    from fastadmin.models.base import admin_dashboard_widgets

    class TestDashboardWidget:
        async def get_data(self, min_x_field=None, max_x_field=None, period_x_field=None):
            return {
                "results": [{"x": "Jan", "y": 1}],
                "min_x_field": min_x_field,
                "max_x_field": max_x_field,
                "period_x_field": period_x_field,
            }

    prev_widgets = admin_dashboard_widgets.copy()
    try:
        admin_dashboard_widgets["TestDashboardWidget"] = TestDashboardWidget()
        r = await client.get("/api/dashboard-widget/TestDashboardWidget?min_x_field=2026-01-01&period_x_field=month")
        assert r.status_code == 200
        assert r.json()["results"] == [{"x": "Jan", "y": 1}]
        assert r.json()["min_x_field"] == "2026-01-01"
        assert r.json()["period_x_field"] == "month"
    finally:
        admin_dashboard_widgets.clear()
        admin_dashboard_widgets.update(prev_widgets)
