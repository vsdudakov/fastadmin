from datetime import datetime, timezone
from uuid import uuid4

import pytest
from flask import Flask
from werkzeug.exceptions import HTTPException

from fastadmin.api.frameworks.flask.api import (
    change,
    change_password,
    delete,
    get,
)
from fastadmin.api.frameworks.flask.app import JSONProvider, exception_handler


async def test_exception_handler():
    assert exception_handler(Exception()) is not None
    assert exception_handler(HTTPException()) is not None


async def test_json_provider():
    today = datetime.now(timezone.utc).date()
    now = datetime.now(timezone.utc)
    uuid = uuid4()
    app = Flask(__name__)
    assert JSONProvider(app).default(today) == today.isoformat()
    assert JSONProvider(app).default(now) == now.isoformat()
    assert JSONProvider(app).default(uuid) == str(uuid)


async def test_flask_get_invalid_id_422():
    """get view raises 422 when id is invalid (empty string)."""
    from tests.environment.flask_app.dev import app as flask_app

    with flask_app.test_request_context(path="/api/retrieve/Event/", method="GET"):
        with pytest.raises(HTTPException) as exc_info:
            await get("Event", "")
        assert exc_info.value.code == 422


async def test_flask_change_password_invalid_id_422():
    """change_password view raises 422 when id is invalid."""
    from tests.environment.flask_app.dev import app as flask_app

    with flask_app.test_request_context(path="/api/change-password/", method="PATCH"):
        with pytest.raises(HTTPException) as exc_info:
            await change_password("")
        assert exc_info.value.code == 422


async def test_flask_change_invalid_id_422():
    """change view raises 422 when id is invalid."""
    from tests.environment.flask_app.dev import app as flask_app

    with flask_app.test_request_context(path="/api/change/Event/", method="PATCH"):
        with pytest.raises(HTTPException) as exc_info:
            await change("Event", "")
        assert exc_info.value.code == 422


async def test_flask_delete_invalid_id_422():
    """delete view raises 422 when id is invalid."""
    from tests.environment.flask_app.dev import app as flask_app

    with flask_app.test_request_context(path="/api/delete/Event/", method="DELETE"):
        with pytest.raises(HTTPException) as exc_info:
            await delete("Event", "")
        assert exc_info.value.code == 422


async def test_flask_dashboard_widget_success():
    from unittest.mock import AsyncMock, patch

    from flask import request as flask_request

    from fastadmin.api.frameworks.flask import api as flask_api
    from tests.environment.flask_app.dev import app as flask_app

    expected = {"labels": ["a"], "values": [1]}

    with flask_app.test_request_context(
        path="/api/dashboard-widget/Event?min_x_field=created_at",
        method="GET",
    ), patch.object(
        flask_api.api_service,
        "dashboard_widget",
        AsyncMock(return_value=expected),
    ) as mock_dashboard:
        response = await flask_api.dashboard_widget("Event")

    assert response == expected
    mock_dashboard.assert_awaited_once_with(
        None,
        "Event",
        min_x_field="created_at",
        max_x_field=None,
        period_x_field=None,
        request=flask_request,
    )
