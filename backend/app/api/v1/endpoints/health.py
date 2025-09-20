"""
Health check endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import structlog

from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: dict
    environment: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check for all services."""
    
    # Check Azure OpenAI availability
    azure_openai_status = "not_configured"
    try:
        from app.services.azure_openai import azure_openai_service
        if azure_openai_service.is_available():
            azure_openai_status = "healthy"
        elif settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
            azure_openai_status = "configured_but_unavailable"
    except Exception as e:
        logger.warning("Error checking Azure OpenAI status", error=str(e))
        azure_openai_status = "error"
    
    # Check Azure Search availability
    azure_search_status = "not_configured"
    if settings.AZURE_SEARCH_ENDPOINT and settings.AZURE_SEARCH_API_KEY:
        azure_search_status = "configured"
    
    # TODO: Add actual Redis health check
    redis_status = "not_implemented"
    
    # TODO: Add actual database health check
    database_status = "not_implemented"
    
    services = {
        "database": database_status,
        "redis": redis_status,
        "azure_openai": azure_openai_status,
        "azure_search": azure_search_status
    }
    
    # Overall status
    overall_status = "healthy"
    if azure_openai_status == "error":
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        services=services,
        environment=settings.ENVIRONMENT
    )


@router.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"message": "pong", "timestamp": datetime.utcnow()}