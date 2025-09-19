"""
Health check endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: dict


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check for all services."""
    
    # TODO: Add actual service health checks
    services = {
        "database": "healthy",
        "redis": "healthy",
        "azure_openai": "not_configured",
        "azure_search": "not_configured"
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        services=services
    )


@router.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"message": "pong", "timestamp": datetime.utcnow()}