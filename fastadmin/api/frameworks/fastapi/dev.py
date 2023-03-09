from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastadmin import fastapi_app as admin_app
from fastadmin.settings import settings

app = FastAPI()
app.mount(f"/{settings.ADMIN_PREFIX}", admin_app)
# CORS
origins = [
    "http://localhost:3030",
    "http://127.0.0.1:3030",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
