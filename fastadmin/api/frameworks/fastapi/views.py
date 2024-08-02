import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from fastadmin.api.helpers import get_template
from fastadmin.settings import ROOT_DIR, settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index():
    """This method is used to render index page.

    :params request: a request object.
    :return: A response object.
    """
    return get_template(
        ROOT_DIR / "templates" / "index.html",
        {
            "ADMIN_PREFIX": settings.ADMIN_PREFIX,
        },
    )
