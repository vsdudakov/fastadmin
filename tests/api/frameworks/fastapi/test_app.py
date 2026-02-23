from fastadmin.api.frameworks.fastapi.app import exception_handler


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
