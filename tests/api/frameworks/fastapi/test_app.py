from unittest.mock import MagicMock

import pytest

from fastadmin.api.frameworks.fastapi.app import exception_handler


async def test_upload_file_empty_filename():
    """upload_file raises 422 when file has no filename (no id in route)."""
    from fastapi import HTTPException

    from fastadmin.api.frameworks.fastapi import api as fastapi_api
    from fastadmin.settings import settings

    request = MagicMock()
    request.cookies = {settings.ADMIN_SESSION_ID_KEY: "sid"}
    mock_file = MagicMock()
    mock_file.filename = ""
    mock_file.read = MagicMock(return_value=b"content")

    with pytest.raises(HTTPException) as exc_info:
        await fastapi_api.upload_file(request, "Event", "file", mock_file)
    assert exc_info.value.status_code == 422
    assert "File name not found" in str(exc_info.value.detail)


async def test_exception_handler():
    assert await exception_handler(None, Exception("Test")) is not None


async def test_fastapi_dashboard_widget_success():
    from unittest.mock import AsyncMock, MagicMock, patch

    from fastadmin.api.frameworks.fastapi import api as fastapi_api
    from fastadmin.settings import settings

    request = MagicMock()
    request.cookies = {settings.ADMIN_SESSION_ID_KEY: "sid"}
    expected = {"labels": ["a"], "values": [1]}

    with patch.object(fastapi_api.api_service, "dashboard_widget", AsyncMock(return_value=expected)) as mock_dashboard:
        response = await fastapi_api.dashboard_widget(request, "Event")

    assert response == expected
    mock_dashboard.assert_awaited_once_with(
        "sid",
        "Event",
        min_x_field=None,
        max_x_field=None,
        period_x_field=None,
        request=request,
    )
