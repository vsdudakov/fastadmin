from django.http import HttpResponse

from fastadmin.api.helpers import get_template
from fastadmin.settings import ROOT_DIR, settings


def index(request):
    """This method is used to render index page.

    :params request: a request object.
    :return: A response object.
    """
    template = get_template(
        ROOT_DIR / "templates" / "index.html",
        {
            "ADMIN_PREFIX": settings.ADMIN_PREFIX,
        },
    )
    return HttpResponse(template)
