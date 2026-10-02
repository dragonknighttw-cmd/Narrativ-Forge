from fastapi import APIRouter

from .routes import auth, episodes, health, ideas, series

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(ideas.router)
api_router.include_router(series.router)
api_router.include_router(episodes.router)
