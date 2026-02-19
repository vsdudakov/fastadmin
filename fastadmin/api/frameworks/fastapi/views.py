import logging
import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from fastadmin.api.helpers import get_template
from fastadmin.settings import ROOT_DIR, settings

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_admin_prefix() -> str:
    """Return admin URL prefix from env at request time so it respects os.environ set after import."""
    return os.getenv("ADMIN_PREFIX", settings.ADMIN_PREFIX)


@router.get("/", response_class=HTMLResponse)
def index():
    """This method is used to render index page.

    :params request: a request object.
    :return: A response object.
    """
    return get_template(
        ROOT_DIR / "templates" / "index.html",
        {
            "ADMIN_PREFIX": _get_admin_prefix(),
        },
    )
