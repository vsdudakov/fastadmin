from datetime import datetime, timedelta, timezone
from io import StringIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import jwt
import pytest

from fastadmin.api.exceptions import AdminApiException
from fastadmin.api.schemas import (
    ExportFormat,
    ExportInputSchema,
    SignInInputSchema,
)
from fastadmin.api.service import ApiService, get_user_id_from_session_id
from fastadmin.models.decorators import action, widget_action
from fastadmin.models.schemas import (
    ActionInputSchema,
    ActionResponseSchema,
    ActionResponseType,
    WidgetActionChartProps,
    WidgetActionInputSchema,
    WidgetActionResponseSchema,
    WidgetActionType,
)
from fastadmin.settings import settings


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


async def test_widget_action_with_sync_handler(monkeypatch):
    """widget_action supports sync handlers decorated with @widget_action."""

    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))

    current_user = {"id": 1, "username": "admin"}
    admin_user_model = SimpleNamespace(get_obj=AsyncMock(return_value=current_user))

    class Admin:
        widget_actions = ("sales_chart",)

        def __init__(self):
            self.context = []

        def set_context(self, request=None, user=None):
            self.context.append((request, user))

        @widget_action(
            widget_action_type=WidgetActionType.ChartLine,
            widget_action_props=WidgetActionChartProps(x_field="x", y_field="y"),
            tab="Analytics",
            title="Sales over time",
            description="Line chart of sales",
        )
        def sales_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
            assert isinstance(payload, WidgetActionInputSchema)
            return WidgetActionResponseSchema(data=[])

    admin = Admin()

    def fake_get_admin_model(model_name):
        if model_name == settings.ADMIN_USER_MODEL:
            return admin_user_model
        return None

    monkeypatch.setattr("fastadmin.api.service.get_admin_model", fake_get_admin_model)
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin)

    request = object()
    result = await ApiService().widget_action(
        "sid",
        "Event",
        "sales_chart",
        WidgetActionInputSchema(query=[]),
        request=request,
    )
    assert isinstance(result, WidgetActionResponseSchema)
    # set_context was bound with request and authenticated user
    assert admin.context == [(request, current_user)]


async def test_widget_action_not_in_widget_actions(monkeypatch):
    """widget_action raises 422 when name is not listed in widget_actions."""

    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))

    current_user = {"id": 1, "username": "admin"}
    admin_user_model = SimpleNamespace(get_obj=AsyncMock(return_value=current_user))
    admin_model = SimpleNamespace(widget_actions=(), set_context=Mock())

    def fake_get_admin_model(model_name):
        if model_name == settings.ADMIN_USER_MODEL:
            return admin_user_model
        return None

    monkeypatch.setattr("fastadmin.api.service.get_admin_model", fake_get_admin_model)
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().widget_action(
            "sid",
            "Event",
            "unknown_widget",
            WidgetActionInputSchema(query=[]),
        )
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "unknown_widget action is not in widget_actions setting."


async def test_widget_action_not_registered(monkeypatch):
    """widget_action raises 422 when attribute is missing or not decorated."""

    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))

    current_user = {"id": 1, "username": "admin"}
    admin_user_model = SimpleNamespace(get_obj=AsyncMock(return_value=current_user))
    # sales_chart is listed but underlying attribute is missing -> not registered
    admin_model = SimpleNamespace(widget_actions=("sales_chart",), set_context=Mock())

    def fake_get_admin_model(model_name):
        if model_name == settings.ADMIN_USER_MODEL:
            return admin_user_model
        return None

    monkeypatch.setattr("fastadmin.api.service.get_admin_model", fake_get_admin_model)
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().widget_action(
            "sid",
            "Event",
            "sales_chart",
            WidgetActionInputSchema(query=[]),
        )
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "sales_chart action is not registered."


async def test_action_accepts_arbitrary_string_ids(monkeypatch):
    """action forwards plain string IDs (non-int/non-uuid) to handlers."""

    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))

    current_user = {"id": 1, "username": "admin"}
    admin_user_model = SimpleNamespace(get_obj=AsyncMock(return_value=current_user))

    captured = {}

    class Admin:
        actions = ("custom_action",)

        def set_context(self, request=None, user=None):
            return None

        @action(description="custom")
        async def custom_action(self, ids):
            captured["ids"] = ids
            return ActionResponseSchema(type=ActionResponseType.MESSAGE, data="ok")

    admin_model = Admin()

    def fake_get_admin_model(model_name):
        if model_name == settings.ADMIN_USER_MODEL:
            return admin_user_model
        return None

    monkeypatch.setattr("fastadmin.api.service.get_admin_model", fake_get_admin_model)
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    response = await ApiService().action(
        "sid",
        "Event",
        "custom_action",
        ActionInputSchema(ids=["custom-string-id"]),
    )

    assert response is not None
    assert response.type == ActionResponseType.MESSAGE
    assert response.data == "ok"
    assert captured["ids"] == ["custom-string-id"]


async def test_widget_action_model_not_registered(monkeypatch):
    """widget_action raises 404 when model is not registered."""

    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))

    current_user = {"id": 1, "username": "admin"}
    admin_user_model = SimpleNamespace(get_obj=AsyncMock(return_value=current_user))

    def fake_get_admin_model(model_name):
        if model_name == settings.ADMIN_USER_MODEL:
            return admin_user_model
        return None

    monkeypatch.setattr("fastadmin.api.service.get_admin_model", fake_get_admin_model)
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: None)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().widget_action(
            "sid",
            "Event",
            "sales_chart",
            WidgetActionInputSchema(query=[]),
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Event model is not registered."


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


async def test_get_raises_500_when_get_obj_raises(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(get_obj=AsyncMock(side_effect=RuntimeError("db error")))
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().get("sid", "Event", 1)
    assert exc_info.value.status_code == 500
    assert "Error getting" in exc_info.value.detail
    assert "db error" in exc_info.value.detail


async def test_add_raises_500_when_save_model_raises(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(save_model=AsyncMock(side_effect=ValueError("validation failed")))
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().add("sid", "Event", {"name": "x"})
    assert exc_info.value.status_code == 500
    assert "Error adding" in exc_info.value.detail
    assert "validation failed" in exc_info.value.detail


async def test_change_password_raises_500_when_get_obj_raises(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))

    async def get_obj_side_effect(id):
        if id == 1:
            return {"id": 1}  # current user for _get_authenticated_user
        raise RuntimeError("db error")  # target user 999

    admin_model = SimpleNamespace(
        get_obj=AsyncMock(side_effect=get_obj_side_effect),
        change_password=AsyncMock(),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().change_password("sid", 999, {"password": "x", "confirm_password": "x"})
    assert exc_info.value.status_code == 500
    assert "Error getting" in exc_info.value.detail


async def test_change_raises_500_when_save_model_raises(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(save_model=AsyncMock(side_effect=ValueError("update failed")))
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().change("sid", "Event", 1, {"name": "y"})
    assert exc_info.value.status_code == 500
    assert "Error changing" in exc_info.value.detail
    assert "update failed" in exc_info.value.detail


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


async def test_upload_file_401(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=None))
    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().upload_file(None, "Event", "file", "x.txt", b"content")
    assert exc_info.value.status_code == 401


async def test_upload_file_404_model_not_registered(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: None)
    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().upload_file("sid", "UnknownModel", "file", "x.txt", b"content")
    assert exc_info.value.status_code == 404
    assert "not registered" in exc_info.value.detail


async def test_upload_file_success(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        set_context=Mock(),
        upload_file=AsyncMock(return_value="/media/x.txt"),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)
    url = await ApiService().upload_file("sid", "Event", "file", "x.txt", b"content")
    assert url == "/media/x.txt"
    admin_model.upload_file.assert_awaited_once_with("file", "x.txt", b"content")


async def test_upload_file_success_with_sync_upload_handler(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    upload_mock = Mock(return_value="/media/x.txt")
    admin_model = SimpleNamespace(
        set_context=Mock(),
        upload_file=upload_mock,
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)

    url = await ApiService().upload_file("sid", "Event", "file", "x.txt", b"content")

    assert url == "/media/x.txt"
    upload_mock.assert_called_once_with("file", "x.txt", b"content")


async def test_upload_file_500_upload_raises(monkeypatch):
    monkeypatch.setattr("fastadmin.api.service.get_user_id_from_session_id", AsyncMock(return_value=1))
    admin_model = SimpleNamespace(
        set_context=Mock(),
        upload_file=AsyncMock(side_effect=OSError("disk full")),
    )
    monkeypatch.setattr("fastadmin.api.service.get_admin_or_admin_inline_model", lambda _model: admin_model)
    with pytest.raises(AdminApiException) as exc_info:
        await ApiService().upload_file("sid", "Event", "file", "x.txt", b"content")
    assert exc_info.value.status_code == 500
    assert "Error uploading file" in exc_info.value.detail
