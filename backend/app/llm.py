"""LLM client configuration for OpenRouter integration."""
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from app.config import get_settings


def get_llm_client(
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> BaseChatModel:
    """Create and configure an LLM client for OpenRouter.
    
    This function creates a LangChain ChatOpenAI instance configured to use
    OpenRouter as the backend. OpenRouter provides access to multiple LLM
    providers through a unified API.
    
    Args:
        model: Model identifier (e.g., "anthropic/claude-3-sonnet")
               If None, uses the model from settings
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response
        
    Returns:
        Configured ChatOpenAI instance
        
    Example:
        >>> llm = get_llm_client()
        >>> response = await llm.ainvoke("สวัสดีครับ")
    """
    settings = get_settings()
    
    # Use provided model or fall back to settings
    model_name = model or settings.openrouter_model
    
    # Create ChatOpenAI client configured for OpenRouter
    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        # Enable streaming for better UX
        streaming=True,
        # Add metadata for OpenRouter
        model_kwargs={
            "extra_headers": {
                "HTTP-Referer": "https://siriform.app",
                "X-Title": "SiriForm Agent"
            }
        }
    )
    
    return llm


def get_supabase_client():
    """Create and configure a Supabase client.
    
    Returns:
        Configured Supabase client instance
        
    Raises:
        ValueError: If Supabase credentials are not configured
    """
    settings = get_settings()
    
    if not settings.supabase_url or not settings.supabase_key:
        raise ValueError(
            "Supabase credentials not configured. "
            "Please set SUPABASE_URL and SUPABASE_KEY in .env file"
        )
    
    from supabase import create_client, Client
    
    supabase: Client = create_client(
        settings.supabase_url,
        settings.supabase_key
    )
    
    return supabase
