"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import games, chat, planning, health, config

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(config.router, prefix="/config", tags=["configuration"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(planning.router, prefix="/planning", tags=["planning"])