from datetime import datetime, timezone
from uuid import uuid4

from flask import Flask
from werkzeug.exceptions import HTTPException

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
