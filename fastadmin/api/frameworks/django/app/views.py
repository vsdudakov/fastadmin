import os

from django.http import HttpResponse

from fastadmin.api.helpers import get_template
from fastadmin.settings import ROOT_DIR, settings


def _get_admin_prefix() -> str:
    """Return admin URL prefix from env at request time so it respects os.environ set after import."""
    return os.getenv("ADMIN_PREFIX", settings.ADMIN_PREFIX)


def index(request):
    """This method is used to render index page.

    :params request: a request object.
    :return: A response object.
    """
    template = get_template(
        ROOT_DIR / "templates" / "index.html",
        {
            "ADMIN_PREFIX": _get_admin_prefix(),
        },
    )
    return HttpResponse(template)
