import logging
import os
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastadmin.api.api import router as api_router
from fastadmin.models.base import BaseModelAdmin
from fastadmin.views import router as views_router

logger = logging.getLogger(__name__)

admin_app = FastAPI(
    openapi_url=None,
)
admin_models: dict[Any, type[BaseModelAdmin]] = {}

current_dir = os.path.dirname(os.path.abspath(__file__))
admin_app.mount(
    "/static",
    StaticFiles(directory=os.path.join(current_dir, "static")),
    name="static",
)
admin_app.include_router(api_router)
admin_app.include_router(views_router)
