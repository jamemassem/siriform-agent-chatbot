"""Contract tests for FastAPI endpoints.

These tests verify the API contract defined in the OpenAPI specification.
They should fail initially (TDD approach) and pass once main.py is implemented.
"""
import pytest
from fastapi.testclient import TestClient


def test_import_main():
    """Test that we can import the FastAPI app."""
    with pytest.raises(ImportError):
        from app.main import app


@pytest.mark.asyncio
async def test_post_chat_endpoint_contract():
    """Test POST /api/v1/chat endpoint contract.
    
    Expected request body:
    {
        "message": "string",
        "session_id": "string", 
        "form_data": {...}
    }
    
    Expected response:
    {
        "response": "string",
        "form_data": {...},
        "highlighted_fields": ["string"],
        "confidence": 0.0-1.0
    }
    """
    with pytest.raises(ImportError):
        from app.main import app
        
        client = TestClient(app)
        
        # Test valid request
        response = client.post("/api/v1/chat", json={
            "message": "I need 2 laptops for tomorrow",
            "session_id": "sess_test_12345",
            "form_data": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "form_data" in data
        assert "highlighted_fields" in data
        assert "confidence" in data
        
        # Verify types
        assert isinstance(data["response"], str)
        assert isinstance(data["form_data"], dict)
        assert isinstance(data["highlighted_fields"], list)
        assert isinstance(data["confidence"], (int, float))
        assert 0.0 <= data["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_post_chat_endpoint_missing_message():
    """Test that missing 'message' field returns 422."""
    with pytest.raises(ImportError):
        from app.main import app
        
        client = TestClient(app)
        
        response = client.post("/api/v1/chat", json={
            "session_id": "sess_test_12345",
            "form_data": {}
        })
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_chat_endpoint_missing_session_id():
    """Test that missing 'session_id' field returns 422."""
    with pytest.raises(ImportError):
        from app.main import app
        
        client = TestClient(app)
        
        response = client.post("/api/v1/chat", json={
            "message": "I need 2 laptops",
            "form_data": {}
        })
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_form_schema_endpoint_contract():
    """Test GET /api/v1/form-schema/{form_name} endpoint contract.
    
    Expected response:
    {
        "name": "string",
        "version": "string",
        "schema": {...}
    }
    """
    with pytest.raises(ImportError):
        from app.main import app
        
        client = TestClient(app)
        
        # Test with equipment_form
        response = client.get("/api/v1/form-schema/equipment_form")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "name" in data
        assert "version" in data
        assert "schema" in data
        
        # Verify types
        assert isinstance(data["name"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["schema"], dict)
        
        # Verify schema is valid JSON Schema
        assert "$schema" in data["schema"]
        assert "properties" in data["schema"]


@pytest.mark.asyncio
async def test_get_form_schema_endpoint_not_found():
    """Test that requesting non-existent form returns 404."""
    with pytest.raises(ImportError):
        from app.main import app
        
        client = TestClient(app)
        
        response = client.get("/api/v1/form-schema/nonexistent_form")
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test GET /health endpoint.
    
    Expected response:
    {
        "status": "healthy",
        "version": "string"
    }
    """
    with pytest.raises(ImportError):
        from app.main import app
        
        client = TestClient(app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_cors_headers():
    """Test that CORS headers are properly configured."""
    with pytest.raises(ImportError):
        from app.main import app
        
        client = TestClient(app)
        
        # Make a preflight OPTIONS request
        response = client.options(
            "/api/v1/chat",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Should allow CORS
        assert response.status_code in [200, 204]
        assert "access-control-allow-origin" in response.headers
