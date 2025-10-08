"""Configuration settings for the application."""
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    app_name: str = "SiriForm Agent Chatbot"
    environment: str = "development"
    debug: bool = True
    
    # OpenRouter API
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-3-sonnet"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_jwt_secret: str = ""
    
    # LangSmith (Observability)
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "siriform-agent"
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings instance with environment variables loaded
    """
    return Settings()


def configure_langsmith():
    """Configure LangSmith tracing if API key is provided."""
    settings = get_settings()
    
    if settings.langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
        print(f"✓ LangSmith tracing enabled for project: {settings.langsmith_project}")
    else:
        print("⚠ LangSmith API key not found - tracing disabled")
