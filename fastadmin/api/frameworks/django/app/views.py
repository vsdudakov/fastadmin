import typing

import jinja2
from django.http import HttpResponse

from fastadmin.settings import ROOT_DIR, settings


def _create_env(directory: str, **env_options: typing.Any) -> "jinja2.Environment":
    loader = jinja2.FileSystemLoader(directory)
    env_options.setdefault("loader", loader)
    env_options.setdefault("autoescape", True)

    return jinja2.Environment(**env_options)  # noqa: S701


async def index(request):
    """This method is used to render index page.

    :params request: a request object.
    :return: A response object.
    """
    env = _create_env(ROOT_DIR / "templates")
    template = env.get_template("index.html")
    content = template.render({"request": request, "settings": settings})

    return HttpResponse(content)
