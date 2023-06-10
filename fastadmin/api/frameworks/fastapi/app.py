import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fastadmin.api.frameworks.fastapi.api import router as api_router
from fastadmin.api.frameworks.fastapi.views import router as views_router
from fastadmin.settings import ROOT_DIR

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FastAdmin App",
    openapi_url=None,
)
app.mount(
    "/static",
    StaticFiles(directory=str(ROOT_DIR / "static")),
    name="static",
)
app.include_router(api_router)
app.include_router(views_router)


@app.exception_handler(Exception)
async def exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"exception": str(exc)},
    )
