from fastapi import APIRouter
from .routes import health, auth, ideas, episodes

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(ideas.router)
api_router.include_router(episodes.router)
