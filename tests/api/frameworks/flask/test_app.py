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


async def test_flask_widget_action_success():
    """Flask widget_action endpoint delegates to ApiService.widget_action."""
    from dataclasses import asdict
    from unittest.mock import AsyncMock, patch

    from fastadmin.api.frameworks.flask import api as flask_api
    from fastadmin.models.schemas import WidgetActionResponseSchema
    from tests.environment.flask_app.dev import app as flask_app

    expected = WidgetActionResponseSchema(data=[])

    with (
        flask_app.test_request_context(
            path="/api/widget-action/Event/sales_chart",
            method="POST",
            json={"query": []},
        ),
        patch.object(
            flask_api.api_service,
            "widget_action",
            AsyncMock(return_value=expected),
        ) as mock_widget,
    ):
        response = await flask_api.widget_action("Event", "sales_chart")

        assert response.json == asdict(expected)
        mock_widget.assert_awaited_once()


async def test_flask_widget_action_admin_exception():
    """Flask widget_action endpoint re-raises AdminApiException as HTTPException."""
    from unittest.mock import AsyncMock, patch

    from fastadmin.api.exceptions import AdminApiException
    from fastadmin.api.frameworks.flask import api as flask_api
    from tests.environment.flask_app.dev import app as flask_app

    with (
        flask_app.test_request_context(
            path="/api/widget-action/Event/sales_chart",
            method="POST",
            json={"query": []},
        ),
        patch.object(
            flask_api.api_service,
            "widget_action",
            AsyncMock(side_effect=AdminApiException(418, detail="boom")),
        ),
        pytest.raises(HTTPException) as exc_info,
    ):
        await flask_api.widget_action("Event", "sales_chart")

    assert exc_info.value.code == 418
    assert "boom" in str(exc_info.value.description)


async def test_flask_upload_file_no_file():
    """upload_file raises 422 when request has no file."""
    from unittest.mock import MagicMock

    from fastadmin.api.frameworks.flask import api as flask_api
    from tests.environment.flask_app.dev import app as flask_app

    with flask_app.test_request_context(
        path="/api/upload-file/Event/file",
        method="POST",
    ):
        request = flask_api.request
        request.files = MagicMock()
        request.files.to_dict.return_value = {}
        request.cookies = {}
        with pytest.raises(HTTPException) as exc_info:
            await flask_api.upload_file("Event", "file")
        assert exc_info.value.code == 422
        assert "File not found" in str(exc_info.value.description)


async def test_flask_upload_file_empty_filename():
    """upload_file raises 422 when file has empty name."""
    from unittest.mock import MagicMock

    from fastadmin.api.frameworks.flask import api as flask_api
    from tests.environment.flask_app.dev import app as flask_app

    with flask_app.test_request_context(
        path="/api/upload-file/Event/file",
        method="POST",
    ):
        request = flask_api.request
        mock_file = MagicMock()
        mock_file.filename = ""
        mock_file.read.return_value = b"content"
        request.files = MagicMock()
        request.files.to_dict.return_value = {"file": mock_file}
        request.cookies = {}
        with pytest.raises(HTTPException) as exc_info:
            await flask_api.upload_file("Event", "file")
        assert exc_info.value.code == 422
        assert "File name not found" in str(exc_info.value.description)


async def test_flask_upload_file_admin_exception():
    """upload_file re-raises AdminApiException as HTTPException."""
    from unittest.mock import AsyncMock, MagicMock, patch

    from fastadmin.api.exceptions import AdminApiException
    from fastadmin.api.frameworks.flask import api as flask_api
    from tests.environment.flask_app.dev import app as flask_app

    with flask_app.test_request_context(
        path="/api/upload-file/Event/file",
        method="POST",
    ):
        request = flask_api.request
        mock_file = MagicMock()
        mock_file.filename = "x.txt"
        mock_file.read.return_value = b"content"
        request.files = MagicMock()
        request.files.to_dict.return_value = {"file": mock_file}
        request.cookies = {}

        with (
            patch.object(
                flask_api.api_service,
                "upload_file",
                AsyncMock(side_effect=AdminApiException(500, detail="upload failed")),
            ),
            pytest.raises(HTTPException) as exc_info,
        ):
            await flask_api.upload_file("Event", "file")
        assert exc_info.value.code == 500
        assert "upload failed" in str(exc_info.value.description)
