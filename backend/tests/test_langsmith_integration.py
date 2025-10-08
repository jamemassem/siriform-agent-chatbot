"""Integration test for LangSmith observability.

This test verifies that LangSmith tracing is properly configured
and can capture agent execution traces.
"""
import pytest
import os
from unittest.mock import patch, MagicMock


def test_langsmith_configuration():
    """Test that LangSmith configuration loads correctly."""
    from app.config import get_settings, configure_langsmith
    
    settings = get_settings()
    
    # Verify settings structure
    assert hasattr(settings, 'langsmith_api_key')
    assert hasattr(settings, 'langsmith_project')
    assert hasattr(settings, 'langchain_tracing_v2')
    assert settings.langsmith_project == "siriform-agent"


def test_langsmith_configuration_with_api_key():
    """Test that LangSmith is properly configured when API key is present."""
    with patch.dict(os.environ, {
        'LANGSMITH_API_KEY': 'ls__test_key_12345',
        'LANGSMITH_PROJECT': 'test-project',
        'LANGCHAIN_TRACING_V2': 'true'
    }):
        from app.config import configure_langsmith
        
        # This should not raise any errors
        configure_langsmith()
        
        # Verify environment variables are set
        assert os.environ.get('LANGCHAIN_API_KEY') == 'ls__test_key_12345'
        assert os.environ.get('LANGCHAIN_PROJECT') == 'test-project'
        assert os.environ.get('LANGCHAIN_TRACING_V2') == 'true'


def test_langsmith_configuration_without_api_key():
    """Test that app works gracefully when LangSmith is not configured."""
    with patch.dict(os.environ, {}, clear=True):
        from app.config import configure_langsmith
        
        # This should not raise any errors, just print a warning
        configure_langsmith()


@pytest.mark.asyncio
async def test_llm_client_creation():
    """Test that LLM client can be created."""
    with patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test_key',
        'OPENROUTER_MODEL': 'anthropic/claude-3-sonnet'
    }):
        from app.llm import get_llm_client
        
        llm = get_llm_client()
        
        # Verify client properties
        assert llm is not None
        assert llm.temperature == 0.7
        assert llm.max_tokens == 2000


@pytest.mark.asyncio
async def test_supabase_client_creation_without_credentials():
    """Test that Supabase client raises error when credentials are missing."""
    with patch.dict(os.environ, {}, clear=True):
        from app.llm import get_supabase_client
        
        with pytest.raises(ValueError, match="Supabase credentials not configured"):
            get_supabase_client()


@pytest.mark.asyncio
async def test_supabase_client_creation_with_credentials():
    """Test that Supabase client can be created with valid credentials."""
    with patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test_key'
    }):
        from app.llm import get_supabase_client
        
        # Mock the create_client function
        with patch('app.llm.create_client') as mock_create:
            mock_create.return_value = MagicMock()
            
            client = get_supabase_client()
            
            # Verify client was created
            assert client is not None
            mock_create.assert_called_once_with(
                'https://test.supabase.co',
                'test_key'
            )
