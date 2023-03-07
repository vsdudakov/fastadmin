import logging
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fastadmin.api.api import router as api_router
from fastadmin.models.base import ModelAdmin
from fastadmin.views import router as views_router

logger = logging.getLogger(__name__)

admin_app = FastAPI(
    openapi_url=None,
)
admin_models: dict[Any, type[ModelAdmin]] = {}

current_dir = os.path.dirname(os.path.abspath(__file__))
admin_app.mount(
    "/static",
    StaticFiles(directory=os.path.join(current_dir, "static")),
    name="static",
)
admin_app.include_router(api_router)
admin_app.include_router(views_router)


@admin_app.exception_handler(Exception)
async def unicorn_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"exception": str(exc)},
    )
