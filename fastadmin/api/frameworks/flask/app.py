import logging
from datetime import date, time

from flask import Blueprint
from flask.json.provider import DefaultJSONProvider
from werkzeug.exceptions import HTTPException

from fastadmin.api.frameworks.flask.api import api_router
from fastadmin.api.frameworks.flask.views import views_router
from fastadmin.settings import ROOT_DIR

logger = logging.getLogger(__name__)


class JSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, date | time):
            return o.isoformat()
        return super().default(o)


app = Blueprint(
    "FastAdmin App",
    __name__,
    url_prefix="/parent",
    static_url_path="/static",
    static_folder=ROOT_DIR / "static",
)
app.register_blueprint(views_router)
app.register_blueprint(api_router)


@app.errorhandler(Exception)
def exception_handler(exc):
    if isinstance(exc, HTTPException):
        return exc
    return {
        "status_code": 500,
        "content": {"exception": str(exc)},
    }
