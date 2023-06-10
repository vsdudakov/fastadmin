import logging

from flask import Blueprint, render_template, request

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
    return render_template("index.html", request=request, settings=settings)
