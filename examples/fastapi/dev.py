from fastapi.middleware.cors import CORSMiddleware

from .app import app

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
