import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fastadmin.api.fastapi.api import router as api_router
from fastadmin.api.fastapi.views import router as views_router
from fastadmin.models.exceptions import AdminModelException
from fastadmin.settings import ROOT_DIR

logger = logging.getLogger(__name__)

app = FastAPI(
    openapi_url=None,
)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(ROOT_DIR, "static")),
    name="static",
)
app.include_router(api_router)
app.include_router(views_router)


@app.exception_handler(AdminModelException)
async def admin_model_exception_handler(_: Request, exc: AdminModelException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"exception": str(exc)},
    )
