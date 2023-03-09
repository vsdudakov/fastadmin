import logging

from flask import Blueprint, abort, render_template, request
from jinja2 import TemplateNotFound

from fastadmin.settings import settings

logger = logging.getLogger(__name__)
views_router = Blueprint(
    "views_router",
    __name__,
)


@views_router.route("/")
def index():
    """This method is used to render index page.

    :return: A response object.
    """
    try:
        return render_template("index.html", **{"request": request, "settings": settings})
    except TemplateNotFound:
        abort(404)
