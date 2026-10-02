from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .db import init_db
from .api.router import api_router

app = FastAPI(title="Narrativ Forge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup() -> None:
    init_db()

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root() -> dict[str, str]:
    return {"service": "narrativ-forge-api", "status": "ok"}
