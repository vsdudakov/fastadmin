from datetime import datetime, timezone
from unittest.mock import patch
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
    from unittest.mock import MagicMock

    from fastadmin.api.frameworks.django.app.api import get

    request = MagicMock()
    request.method = "GET"
    response = await get(request, "Event", "")
    assert response.status_code == 422


async def test_django_change_password_invalid_id_422():
    """change_password view returns 422 when id is invalid."""
    from unittest.mock import MagicMock

    from fastadmin.api.frameworks.django.app.api import change_password

    request = MagicMock()
    request.method = "PATCH"
    response = await change_password(request, "")
    assert response.status_code == 422


async def test_django_change_invalid_id_422():
    """change view returns 422 when id is invalid."""
    from unittest.mock import MagicMock

    from fastadmin.api.frameworks.django.app.api import change

    request = MagicMock()
    request.method = "PATCH"
    response = await change(request, "Event", "")
    assert response.status_code == 422


async def test_django_delete_invalid_id_422():
    """delete view returns 422 when id is invalid."""
    from unittest.mock import MagicMock

    from fastadmin.api.frameworks.django.app.api import delete

    request = MagicMock()
    request.method = "DELETE"
    response = await delete(request, "Event", "")
    assert response.status_code == 422


async def test_django_dashboard_widget_405():
    """dashboard_widget returns 405 when method is not GET."""
    from unittest.mock import MagicMock

    from fastadmin.api.frameworks.django.app.api import dashboard_widget

    request = MagicMock()
    request.method = "POST"
    response = await dashboard_widget(request, "SomeWidget")
    assert response.status_code == 405


async def test_django_dashboard_widget_404(session_id):
    """dashboard_widget returns 404 when widget model is not registered."""
    from django.http import HttpRequest

    from fastadmin.api.frameworks.django.app.api import dashboard_widget
    from fastadmin.settings import settings

    request = HttpRequest()
    request.method = "GET"
    request.COOKIES = {settings.ADMIN_SESSION_ID_KEY: session_id}
    response = await dashboard_widget(request, "NonExistentWidget")
    assert response.status_code == 404


async def test_django_dashboard_widget_success():
    from unittest.mock import AsyncMock, MagicMock, patch

    from fastadmin.api.frameworks.django.app import api as django_api_module
    from fastadmin.api.frameworks.django.app.api import dashboard_widget
    from fastadmin.settings import settings

    request = MagicMock()
    request.method = "GET"
    request.GET.dict.return_value = {"min_x_field": "created_at"}
    request.COOKIES = {settings.ADMIN_SESSION_ID_KEY: "sid"}

    expected = {"labels": ["a"], "values": [1]}
    with patch.object(
        django_api_module.api_service,
        "dashboard_widget",
        AsyncMock(return_value=expected),
    ) as mock_dashboard:
        response = await dashboard_widget(request, "Event")

    assert response.status_code == 200
    assert response.content == b'{"labels": ["a"], "values": [1]}'
    mock_dashboard.assert_awaited_once_with(
        "sid",
        "Event",
        min_x_field="created_at",
        max_x_field=None,
        period_x_field=None,
    )
