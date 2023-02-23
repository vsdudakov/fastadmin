import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import router as api_router
from settings import settings
from views import router as views_router

logger = logging.getLogger(__name__)

admin_app = FastAPI()


@admin_app.on_event("startup")
async def startup():
    pass


@admin_app.on_event("shutdown")
async def shutdown():
    pass


admin_app.mount(
    f"/{settings.ADMIN_PREFIX}/static",
    StaticFiles(directory="static"),
    name="static",
)
admin_app.include_router(api_router, prefix=f"/{settings.ADMIN_PREFIX}")
admin_app.include_router(views_router, prefix=f"/{settings.ADMIN_PREFIX}")


# CORS
origins = [
    "http://localhost:3030",
    "http://127.0.0.1:3030",
]

admin_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
