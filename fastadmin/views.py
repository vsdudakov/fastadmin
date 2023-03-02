import logging
import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastadmin.settings import settings

current_dir = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """This method is used to render index page.

    :params request: a request object.
    :return: A response object.
    """
    return templates.TemplateResponse("index.html", {"request": request, "settings": settings})
