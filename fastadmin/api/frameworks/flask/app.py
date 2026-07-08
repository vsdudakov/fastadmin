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
    url_prefix="",
    static_url_path="/static",
    static_folder=ROOT_DIR / "static",
)
app.register_blueprint(views_router)
app.register_blueprint(api_router)


@app.errorhandler(Exception)
def exception_handler(exc):
    if isinstance(exc, HTTPException):
        if exc.response is not None:
            # abort(Response(...)) attached a fully-formed response; pass it
            # through untouched instead of replacing it with a generic error.
            return exc
        # Return API errors as JSON {"detail": ...} with the proper HTTP status
        # so the shared React frontend can read the message (matching the Django
        # and FastAPI integrations), instead of werkzeug's default HTML page.
        # Keep the exception's headers (Allow, WWW-Authenticate, Retry-After, ...)
        # apart from its text/html Content-Type, which the JSON body replaces.
        headers = [(k, v) for k, v in exc.get_headers() if k.lower() != "content-type"]
        return {"detail": exc.description}, exc.code or 500, headers
    # Unhandled server error: log it (with traceback — this is the only place it
    # is captured) but never leak internals to the client, and return a real
    # HTTP 500 (a bare dict would be sent as HTTP 200).
    logger.error("Unhandled admin error: %s", exc, exc_info=exc)
    return {"detail": "Internal server error."}, 500
