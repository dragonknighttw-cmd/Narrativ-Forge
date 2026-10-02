from fastapi import APIRouter

from .routes import assets, auth, episodes, health, ideas, jobs, scenes, scripts, series, subtitles, review, export

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(ideas.router)
api_router.include_router(series.router)
api_router.include_router(episodes.router)
api_router.include_router(scripts.router)
api_router.include_router(scripts.script_router)
api_router.include_router(scenes.router)
api_router.include_router(scenes.scene_router)
api_router.include_router(assets.router)
api_router.include_router(assets.asset_router)
api_router.include_router(jobs.router)
api_router.include_router(subtitles.router)
api_router.include_router(review.router)
api_router.include_router(export.router)
