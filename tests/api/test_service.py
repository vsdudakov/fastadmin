from datetime import datetime, timedelta, timezone
from io import StringIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import jwt
import pytest

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.schemas import ExportFormat, ExportInputSchema, SignInInputSchema
from fastadmin.api.service import ApiService, convert_id, get_user_id_from_session_id
from fastadmin.models.base import admin_dashboard_widgets
from fastadmin.settings import settings


def test_convert_id():
    assert convert_id("1") == 1
    assert convert_id("1000") == 1000
    assert convert_id(1000) == 1000
    assert convert_id("123e4567-e89b-12d3-a456-426614174000") == UUID("123e4567-e89b-12d3-a456-426614174000")
    assert convert_id(UUID("123e4567-e89b-12d3-a456-426614174000")) == UUID("123e4567-e89b-12d3-a456-426614174000")
    assert convert_id("invalid") is None


async def test_get_user_id_from_session_id_without_user_id(monkeypatch):
    admin_model = SimpleNamespace(get_obj=AsyncMock(return_value={"id": 1}))
    monkeypatch.setattr("fastadmin.api.service.get_admin_model", lambda _model: admin_model)

    token = jwt.encode(
        {"session_expired_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()},
        settings.ADMIN_SECRET_KEY,
        algorithm="HS256",
    )
    assert await get_user_id_from_session_id(token) is None


async def test_sign_in_converts_uuid_to_string(monkeypatch):
    user_id = uuid4()
    admin_model = SimpleNamespace(authenticate=AsyncMock(return_value=user_id))
    monkeypatch.setattr("fastadmin.api.service.get_admin_model", lambda _model: admin_model)

    token = await ApiService().sign_in(None, SignInInputSchema(username="u", password="p"))
    payload = jwt.decode(token, settings.ADMIN_SECRET_KEY, algorithms=["HS256"])
    assert payload["user_id"] == str(user_id)


async def test_dashboard_widget_with_sync_get_data(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))

    class SyncWidget:
        def get_data(self, min_x_field=None, max_x_field=None, period_x_field=None):
            return {
                "results": [{"x": "A", "y": 1}],
                "min_x_field": min_x_field,
                "max_x_field": max_x_field,
                "period_x_field": period_x_field,
            }

    monkeypatch.setitem(admin_dashboard_widgets, "SyncWidget", SyncWidget())
    result = await ApiService().dashboard_widget(
        "sid",
        "SyncWidget",
        min_x_field="a",
        max_x_field="b",
        period_x_field="month",
    )
    assert result["results"] == [{"x": "A", "y": 1}]


async def test_list_skips_excluded_filter_fields(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        search_fields=[],
        ordering=[],
        list_select_related=[],
        get_fields_for_serialize=lambda: ["name"],
        get_model_fields_with_widget_types=list,
        get_list=AsyncMock(return_value=([{"name": "x"}], 1)),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    items, total = await ApiService().list("sid", "Event", filters={"search": "abc"})
    assert total == 1
    assert items == [{"name": "x"}]
    admin_model.get_list.assert_awaited_once_with(
        offset=0,
        limit=10,
        search=None,
        sort_by=None,
        filters={},
    )


async def test_list_binds_request_and_user_context(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    current_user = {"id": 1, "username": "admin"}
    monkeypatch.setattr(
        "fastadmin.api.service.get_admin_model",
        lambda _model: SimpleNamespace(get_obj=AsyncMock(return_value=current_user)),
    )

    set_context = Mock()
    admin_model = SimpleNamespace(
        search_fields=[],
        ordering=[],
        list_select_related=[],
        get_fields_for_serialize=lambda: ["name"],
        get_model_fields_with_widget_types=list,
        get_list=AsyncMock(return_value=([{"name": "x"}], 1)),
        set_context=set_context,
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    request = object()
    items, total = await ApiService().list("sid", "Event", request=request)
    assert total == 1
    assert items == [{"name": "x"}]
    set_context.assert_called_once_with(request=request, user=current_user)


async def test_change_password_admin_model_not_registered(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    monkeypatch.setattr("fastadmin.api.service.get_admin_model", lambda _model: None)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().change_password("sid", 1, {"password": "x", "confirm_password": "x"})
    assert exc_info.value.status_code == 404


async def test_change_password_mismatch(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    monkeypatch.setattr("fastadmin.api.service.get_admin_model", lambda _model: SimpleNamespace())

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().change_password("sid", 1, {"password": "x", "confirm_password": "y"})
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Passwords do not match"


async def test_change_password_method_not_registered(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(get_obj=AsyncMock(return_value={"id": 1}))
    monkeypatch.setattr("fastadmin.api.service.get_admin_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().change_password("sid", 1, {"password": "x", "confirm_password": "x"})
    assert exc_info.value.status_code == 404
    assert "has no change_password method" in exc_info.value.detail


async def test_change_password_handles_change_password_value_error(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))

    async def raise_value_error(_id, _password):
        raise ValueError("not found")

    admin_model = SimpleNamespace(
        get_obj=AsyncMock(return_value={"id": 1}),
        change_password=raise_value_error,
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().change_password("sid", 1, {"password": "x", "confirm_password": "x"})
    assert exc_info.value.status_code == 404


async def test_export_invalid_search_field(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        search_fields=["bad_field"],
        ordering=[],
        get_fields_for_serialize=lambda: ["name"],
        get_model_fields_with_widget_types=list,
        get_export=AsyncMock(return_value=StringIO("")),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().export("sid", "Event", ExportInputSchema(), search="q")
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Search by bad_field is not allowed"


async def test_export_invalid_filter_field(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        search_fields=[],
        ordering=[],
        get_fields_for_serialize=lambda: ["name"],
        get_model_fields_with_widget_types=list,
        get_export=AsyncMock(return_value=StringIO("")),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().export("sid", "Event", ExportInputSchema(), filters={"bad__exact": "x"})
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Filter by bad__exact is not allowed"


async def test_export_invalid_sort_by(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        search_fields=[],
        ordering=[],
        get_fields_for_serialize=lambda: ["name"],
        get_model_fields_with_widget_types=list,
        get_export=AsyncMock(return_value=StringIO("")),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().export("sid", "Event", ExportInputSchema(), sort_by="-bad")
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Sort by -bad is not allowed"


async def test_export_invalid_default_ordering(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        search_fields=[],
        ordering=["-bad"],
        get_fields_for_serialize=lambda: ["name"],
        get_model_fields_with_widget_types=list,
        get_export=AsyncMock(return_value=StringIO("")),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().export("sid", "Event", ExportInputSchema())
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Sort by -bad is not allowed"


async def test_export_json_format(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        search_fields=[],
        ordering=[],
        get_fields_for_serialize=lambda: ["name"],
        get_model_fields_with_widget_types=list,
        get_export=AsyncMock(return_value=StringIO("{}")),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    file_name, content_type, stream = await ApiService().export(
        "sid",
        "Event",
        ExportInputSchema(format=ExportFormat.JSON),
    )
    assert file_name == "Event.json"
    assert content_type == "text/plain"
    assert stream is not None


async def test_export_skips_excluded_filters(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        search_fields=[],
        ordering=[],
        get_fields_for_serialize=lambda: ["name"],
        get_model_fields_with_widget_types=list,
        get_export=AsyncMock(return_value=StringIO("ok")),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    _file_name, _content_type, _stream = await ApiService().export(
        "sid",
        "Event",
        ExportInputSchema(),
        filters={"offset": "1"},
    )

    admin_model.get_export.assert_awaited_once_with(
        ExportFormat.CSV,
        offset=0,
        limit=1000,
        search=None,
        sort_by=None,
        filters={},
    )
