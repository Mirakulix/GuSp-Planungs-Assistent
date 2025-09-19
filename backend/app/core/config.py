"""
Configuration settings for the Pfadi AI Assistant application.
"""

from typing import List, Optional
from pydantic import BaseSettings, AnyHttpUrl, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project metadata
    PROJECT_NAME: str = "Pfadi AI Assistant"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI-powered planning assistant for Scout leaders"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:8080",  # Alternative frontend port
    ]
    
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = "sqlite:///./pfadi_assistant.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_EMBEDDING_DEPLOYMENT_NAME: str = "text-embedding-ada-002"
    
    # Azure AI Search
    AZURE_SEARCH_ENDPOINT: Optional[str] = None
    AZURE_SEARCH_API_KEY: Optional[str] = None
    AZURE_SEARCH_INDEX_NAME: str = "pfadi-games"
    
    # External APIs
    WEATHER_API_KEY: Optional[str] = None
    GOOGLE_DRIVE_API_KEY: Optional[str] = None
    
    # Communication
    SENDGRID_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    
    # File paths
    DATA_DIR: Path = Path("data")
    LOCAL_DATA_DIR: Path = DATA_DIR / "local"
    GOOGLE_DRIVE_DATA_DIR: Path = DATA_DIR / "google_drive"
    
    @validator("DATA_DIR", "LOCAL_DATA_DIR", "GOOGLE_DRIVE_DATA_DIR", pre=True)
    def resolve_paths(cls, v):
        """Resolve paths relative to the application root."""
        if isinstance(v, str):
            v = Path(v)
        if not v.is_absolute():
            # Make relative to the project root (where main.py is located)
            app_root = Path(__file__).parent.parent.parent
            v = app_root / v
        return v.resolve()
    
    # Logging
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"
    
    # Feature flags
    ENABLE_CHATBOT: bool = True
    ENABLE_GAME_SEARCH: bool = True
    ENABLE_PLANNING: bool = True
    ENABLE_CAMP_PLANNING: bool = False  # Will be enabled later
    ENABLE_COMMUNICATION: bool = False  # Will be enabled later
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure data directories exist
settings.LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.GOOGLE_DRIVE_DATA_DIR.mkdir(parents=True, exist_ok=True)