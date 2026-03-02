from unittest.mock import AsyncMock, MagicMock, patch

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


async def test_fastapi_widget_action_success():
    """FastAPI widget_action endpoint delegates to ApiService.widget_action."""
    from dataclasses import asdict

    from fastadmin.api.frameworks.fastapi import api as fastapi_api
    from fastadmin.models.schemas import WidgetActionInputSchema, WidgetActionResponseSchema
    from fastadmin.settings import settings

    request = MagicMock()
    request.cookies = {settings.ADMIN_SESSION_ID_KEY: "sid"}
    payload = WidgetActionInputSchema(query=[])
    expected = WidgetActionResponseSchema(data=[])

    with patch.object(
        fastapi_api.api_service,
        "widget_action",
        AsyncMock(return_value=expected),
    ) as mock_widget:
        response = await fastapi_api.widget_action(request, "Event", "sales_chart", payload)

    assert response == asdict(expected)
    mock_widget.assert_awaited_once_with(
        "sid",
        "Event",
        "sales_chart",
        payload,
        request=request,
    )


async def test_fastapi_widget_action_admin_exception():
    """FastAPI widget_action endpoint converts AdminApiException to HTTPException."""
    from fastapi import HTTPException

    from fastadmin.api.exceptions import AdminApiException
    from fastadmin.api.frameworks.fastapi import api as fastapi_api
    from fastadmin.models.schemas import WidgetActionInputSchema
    from fastadmin.settings import settings

    request = MagicMock()
    request.cookies = {settings.ADMIN_SESSION_ID_KEY: "sid"}
    payload = WidgetActionInputSchema(query=[])

    with pytest.raises(HTTPException) as exc_info, patch.object(
        fastapi_api.api_service,
        "widget_action",
        AsyncMock(side_effect=AdminApiException(418, detail="boom")),
    ) as mock_widget:
        await fastapi_api.widget_action(request, "Event", "sales_chart", payload)

    assert exc_info.value.status_code == 418
    assert "boom" in str(exc_info.value.detail)
    mock_widget.assert_awaited_once_with(
        "sid",
        "Event",
        "sales_chart",
        payload,
        request=request,
    )
