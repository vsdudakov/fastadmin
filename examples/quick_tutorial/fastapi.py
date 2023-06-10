from fastapi import FastAPI

from fastadmin import fastapi_app as admin_app

app = FastAPI()

app.mount("/admin", admin_app)
