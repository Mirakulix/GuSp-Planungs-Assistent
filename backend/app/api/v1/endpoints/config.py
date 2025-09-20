"""
Configuration and setup endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List
import structlog

from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()


class ConfigStatus(BaseModel):
    configured: bool
    missing_variables: List[str]
    environment: str
    features: Dict[str, bool]


class AzureConfigGuide(BaseModel):
    steps: List[Dict[str, str]]
    required_variables: List[Dict[str, str]]
    test_endpoints: List[str]


@router.get("/status", response_model=ConfigStatus)
async def get_config_status():
    """Get the current configuration status and missing variables."""
    
    # Check required Azure variables
    required_vars = [
        ("AZURE_OPENAI_ENDPOINT", settings.AZURE_OPENAI_ENDPOINT),
        ("AZURE_OPENAI_API_KEY", settings.AZURE_OPENAI_API_KEY),
        ("AZURE_OPENAI_DEPLOYMENT_NAME", settings.AZURE_OPENAI_DEPLOYMENT_NAME),
        ("AZURE_EMBEDDING_DEPLOYMENT_NAME", settings.AZURE_EMBEDDING_DEPLOYMENT_NAME),
    ]
    
    missing_variables = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing_variables.append(var_name)
    
    # Optional but recommended variables
    optional_vars = [
        ("AZURE_SEARCH_ENDPOINT", settings.AZURE_SEARCH_ENDPOINT),
        ("AZURE_SEARCH_API_KEY", settings.AZURE_SEARCH_API_KEY),
    ]
    
    for var_name, var_value in optional_vars:
        if not var_value:
            missing_variables.append(f"{var_name} (optional)")
    
    configured = len([v for v in required_vars if v[1]]) == len(required_vars)
    
    return ConfigStatus(
        configured=configured,
        missing_variables=missing_variables,
        environment=settings.ENVIRONMENT,
        features={
            "chatbot": settings.ENABLE_CHATBOT,
            "game_search": settings.ENABLE_GAME_SEARCH,
            "planning": settings.ENABLE_PLANNING,
            "camp_planning": settings.ENABLE_CAMP_PLANNING,
            "communication": settings.ENABLE_COMMUNICATION
        }
    )


@router.get("/azure/guide", response_model=AzureConfigGuide)
async def get_azure_setup_guide():
    """Get a step-by-step guide for setting up Azure services."""
    
    return AzureConfigGuide(
        steps=[
            {
                "step": "1",
                "title": "Azure OpenAI Resource erstellen",
                "description": "Erstelle eine Azure OpenAI Resource in deinem Azure Portal",
                "action": "Gehe zu portal.azure.com → Create a resource → Azure OpenAI"
            },
            {
                "step": "2", 
                "title": "GPT-4 Deployment erstellen",
                "description": "Erstelle ein Deployment für GPT-4 in deiner Azure OpenAI Resource",
                "action": "Azure OpenAI Studio → Deployments → Create new deployment → gpt-4"
            },
            {
                "step": "3",
                "title": "Embedding Deployment erstellen",
                "description": "Erstelle ein Deployment für text-embedding-ada-002",
                "action": "Azure OpenAI Studio → Deployments → Create new deployment → text-embedding-ada-002"
            },
            {
                "step": "4",
                "title": "API Keys kopieren",
                "description": "Kopiere den API Key und Endpoint aus deiner Azure OpenAI Resource",
                "action": "Azure Portal → deine OpenAI Resource → Keys and Endpoint"
            },
            {
                "step": "5",
                "title": "Environment Variables setzen",
                "description": "Trage die Werte in deine .env Datei ein",
                "action": "Bearbeite .env mit den kopierten Werten"
            },
            {
                "step": "6",
                "title": "Service neu starten",
                "description": "Starte den Backend-Service neu, um die neuen Einstellungen zu laden",
                "action": "docker-compose restart backend"
            }
        ],
        required_variables=[
            {
                "name": "AZURE_OPENAI_ENDPOINT",
                "description": "Der Endpoint deiner Azure OpenAI Resource",
                "example": "https://your-resource-name.openai.azure.com/"
            },
            {
                "name": "AZURE_OPENAI_API_KEY",
                "description": "Der API Key deiner Azure OpenAI Resource",
                "example": "1234567890abcdef1234567890abcdef"
            },
            {
                "name": "AZURE_OPENAI_DEPLOYMENT_NAME",
                "description": "Name deines GPT-4 Deployments",
                "example": "gpt-4"
            },
            {
                "name": "AZURE_EMBEDDING_DEPLOYMENT_NAME",
                "description": "Name deines Embedding Deployments",
                "example": "text-embedding-ada-002"
            }
        ],
        test_endpoints=[
            "/api/v1/health",
            "/api/v1/chat/status",
            "/api/v1/config/status"
        ]
    )


@router.get("/azure/test")
async def test_azure_connection():
    """Test the Azure OpenAI connection."""
    
    try:
        from app.services.azure_openai import azure_openai_service
        
        if not azure_openai_service.is_available():
            return {
                "success": False,
                "message": "Azure OpenAI ist nicht konfiguriert oder nicht verfügbar",
                "details": "Prüfe deine Umgebungsvariablen in der .env Datei"
            }
        
        # Try a simple chat completion
        test_response = await azure_openai_service.chat_completion(
            messages=[
                {"role": "system", "content": "Du bist ein Test-Assistent."},
                {"role": "user", "content": "Sage 'Test erfolgreich' auf Deutsch."}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        if test_response.get("message"):
            return {
                "success": True,
                "message": "Azure OpenAI Verbindung erfolgreich!",
                "test_response": test_response.get("message"),
                "usage": test_response.get("usage", {})
            }
        else:
            return {
                "success": False,
                "message": "Azure OpenAI antwortet nicht wie erwartet",
                "details": test_response
            }
            
    except Exception as e:
        logger.error("Azure connection test failed", error=str(e))
        return {
            "success": False,
            "message": "Fehler beim Testen der Azure OpenAI Verbindung",
            "error": str(e)
        }


@router.get("/env/template")
async def get_env_template():
    """Get a template for the .env file with current status."""
    
    template_lines = [
        "# Azure OpenAI Configuration",
        f"AZURE_OPENAI_ENDPOINT={settings.AZURE_OPENAI_ENDPOINT or 'https://your-resource-name.openai.azure.com/'}",
        f"AZURE_OPENAI_API_KEY={settings.AZURE_OPENAI_API_KEY or 'your-azure-openai-api-key'}",
        f"AZURE_OPENAI_DEPLOYMENT_NAME={settings.AZURE_OPENAI_DEPLOYMENT_NAME}",
        f"AZURE_EMBEDDING_DEPLOYMENT_NAME={settings.AZURE_EMBEDDING_DEPLOYMENT_NAME}",
        "",
        "# Azure AI Search (Optional)",
        f"AZURE_SEARCH_ENDPOINT={settings.AZURE_SEARCH_ENDPOINT or 'https://your-search-service.search.windows.net'}",
        f"AZURE_SEARCH_API_KEY={settings.AZURE_SEARCH_API_KEY or 'your-search-api-key'}",
        f"AZURE_SEARCH_INDEX_NAME={settings.AZURE_SEARCH_INDEX_NAME}",
        "",
        "# Application Settings",
        f"SECRET_KEY={settings.SECRET_KEY}",
        f"ENVIRONMENT={settings.ENVIRONMENT}",
        f"DEBUG={settings.DEBUG}",
        "",
        "# Database",
        f"DATABASE_URL={settings.DATABASE_URL}",
        "",
        "# Redis",
        f"REDIS_URL={settings.REDIS_URL}"
    ]
    
    return {
        "template": "\n".join(template_lines),
        "current_status": await get_config_status()
    }