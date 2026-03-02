from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastadmin.api.frameworks.django.app import api as django_api


async def test_json_provider():
    from fastadmin.api.frameworks.django.app.api import JsonEncoder

    today = datetime.now(timezone.utc).date()
    now = datetime.now(timezone.utc)
    uuid = uuid4()
    assert JsonEncoder().default(today) == today.isoformat()
    assert JsonEncoder().default(now) == now.isoformat()
    assert JsonEncoder().default(uuid) == str(uuid)


async def test_json_encoder_field_file_value_error():
    """JsonEncoder returns None when FieldFile.url raises ValueError."""
    # Use a type that passes isinstance(o, FieldFile) when we patch FieldFile/ImageFieldFile
    patched_file = type("FieldFile", (), {})

    class MockFieldFile(patched_file):
        @property
        def url(self):
            raise ValueError("no file")

    with patch.object(django_api, "FieldFile", patched_file), patch.object(django_api, "ImageFieldFile", patched_file):
        result = django_api.JsonEncoder().default(MockFieldFile())
    assert result is None


async def test_django_get_invalid_id_422():
    """get view returns 422 when id is invalid (e.g. empty string)."""
    from fastadmin.api.frameworks.django.app.api import get

    request = MagicMock()
    request.method = "GET"
    response = await get(request, "Event", "")
    assert response.status_code == 422


async def test_django_change_password_invalid_id_422():
    """change_password view returns 422 when id is invalid."""
    from fastadmin.api.frameworks.django.app.api import change_password

    request = MagicMock()
    request.method = "PATCH"
    response = await change_password(request, "")
    assert response.status_code == 422


async def test_django_change_invalid_id_422():
    """change view returns 422 when id is invalid."""
    from fastadmin.api.frameworks.django.app.api import change

    request = MagicMock()
    request.method = "PATCH"
    response = await change(request, "Event", "")
    assert response.status_code == 422


async def test_django_delete_invalid_id_422():
    """delete view returns 422 when id is invalid."""
    from fastadmin.api.frameworks.django.app.api import delete

    request = MagicMock()
    request.method = "DELETE"
    response = await delete(request, "Event", "")
    assert response.status_code == 422


async def test_django_widget_action_405():
    """widget_action returns 405 when method is not POST."""
    from fastadmin.api.frameworks.django.app.api import widget_action

    request = MagicMock()
    request.method = "GET"
    response = await widget_action(request, "Event", "sales_chart")
    assert response.status_code == 405


async def test_django_widget_action_success():
    """widget_action delegates to ApiService.widget_action and serializes response."""
    from dataclasses import asdict

    from fastadmin.api.frameworks.django.app import api as django_api_module
    from fastadmin.api.frameworks.django.app.api import widget_action
    from fastadmin.models.schemas import WidgetActionResponseSchema
    from fastadmin.settings import settings

    request = MagicMock()
    request.method = "POST"
    request.body = b'{"query": []}'
    request.COOKIES = {settings.ADMIN_SESSION_ID_KEY: "sid"}

    expected = WidgetActionResponseSchema(data=[])
    with patch.object(
        django_api_module.api_service,
        "widget_action",
        AsyncMock(return_value=expected),
    ) as mock_widget:
        response = await widget_action(request, "Event", "sales_chart")

    assert response.status_code == 200
    assert response.content == django_api.JsonResponse(asdict(expected)).content
    mock_widget.assert_awaited_once()


async def test_django_widget_action_admin_exception():
    """widget_action returns JsonResponse with AdminApiException details."""
    from fastadmin.api.exceptions import AdminApiException
    from fastadmin.api.frameworks.django.app import api as django_api_module
    from fastadmin.api.frameworks.django.app.api import widget_action
    from fastadmin.settings import settings

    request = MagicMock()
    request.method = "POST"
    request.body = b'{"query": []}'
    request.COOKIES = {settings.ADMIN_SESSION_ID_KEY: "sid"}

    with patch.object(
        django_api_module.api_service,
        "widget_action",
        AsyncMock(side_effect=AdminApiException(418, detail="boom")),
    ):
        response = await widget_action(request, "Event", "sales_chart")

    assert response.status_code == 418
    assert response.content == django_api.JsonResponse({"detail": "boom"}).content


async def test_django_upload_file_missing_file_400():
    """upload_file returns 400 when request has no file."""
    from unittest.mock import MagicMock

    from fastadmin.api.frameworks.django.app.api import upload_file

    request = MagicMock()
    request.method = "POST"
    request.FILES.get.return_value = None
    response = await upload_file(request, "Event", "file")
    assert response.status_code == 400


async def test_django_upload_file_success():
    """upload_file returns JSON response with uploaded file url (no id in route)."""
    from unittest.mock import AsyncMock, MagicMock, patch

    from fastadmin.api.frameworks.django.app import api as django_api_module
    from fastadmin.api.frameworks.django.app.api import upload_file
    from fastadmin.settings import settings

    request = MagicMock()
    request.method = "POST"
    request.COOKIES = {settings.ADMIN_SESSION_ID_KEY: "sid"}

    file = MagicMock()
    file.name = "x.txt"
    file.read.return_value = b"content"
    request.FILES.get.return_value = file

    with patch.object(
        django_api_module.api_service,
        "upload_file",
        AsyncMock(return_value="/media/x.txt"),
    ) as mock_upload:
        response = await upload_file(request, "Event", "file")

    assert response.status_code == 200
    assert response.content == b'"/media/x.txt"'
    mock_upload.assert_awaited_once_with(
        "sid",
        "Event",
        "file",
        "x.txt",
        b"content",
        request=request,
    )
