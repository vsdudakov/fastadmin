import logging
import os

from flask import Blueprint

from fastadmin.api.helpers import get_template
from fastadmin.settings import ROOT_DIR, settings

logger = logging.getLogger(__name__)
views_router = Blueprint(
    "views_router",
    __name__,
)


def _get_admin_prefix() -> str:
    """Return admin URL prefix from env at request time so it respects os.environ set after import."""
    return os.getenv("ADMIN_PREFIX", settings.ADMIN_PREFIX)


@views_router.route("/")
def index():
    """This method is used to render index page.

    :return: A response object.
    """
    return get_template(
        ROOT_DIR / "templates" / "index.html",
        {
            "ADMIN_PREFIX": _get_admin_prefix(),
        },
    )
