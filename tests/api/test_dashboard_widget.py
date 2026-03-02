"""Tests for widget action API (covers exception paths in FastAPI/Flask/Django)."""


async def test_widget_action_401(client):
    """Widget action returns 401 when not authenticated."""
    r = await client.post("/api/widget-action/Event/sales_chart", json={"query": []})
    assert r.status_code == 401


async def test_widget_action_404(session_id, client):
    """Widget action returns 404 when model is not registered."""
    assert session_id
    r = await client.post("/api/widget-action/NonExistentModel/sales_chart", json={"query": []})
    assert r.status_code == 404


async def test_widget_action_200(session_id, client):
    """Widget action returns data for a registered model/widget."""
    assert session_id

    from dataclasses import asdict

    from fastadmin.models.base import ModelAdmin, admin_models
    from fastadmin.models.decorators import widget_action
    from fastadmin.models.schemas import WidgetActionInputSchema, WidgetActionResponseSchema

    class Model:
        pass

    expected_data = [{"date": "2026-01-01", "total_sales": 100, "status": "Pending"}]

    class TestAdmin(ModelAdmin):
        widget_actions = ("sales_chart",)

        @widget_action()
        async def sales_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
            return WidgetActionResponseSchema(data=expected_data)

    prev_widgets = admin_models.copy()
    try:
        admin_models[Model] = TestAdmin(Model)
        r = await client.post("/api/widget-action/Model/sales_chart", json={"query": []})
        assert r.status_code == 200
        assert r.json() == asdict(WidgetActionResponseSchema(data=expected_data))
    finally:
        admin_models.clear()
        admin_models.update(prev_widgets)
