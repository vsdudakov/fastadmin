from fastapi import FastAPI

from fastadmin import fastapi_app as admin_app
from fastadmin.settings import settings

app = FastAPI()
app.mount(f"/{settings.PREFIX}", admin_app)
