"""
Test configuration and fixtures for agent tools tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    client = MagicMock()
    client.table.return_value = client
    client.select.return_value = client
    client.insert.return_value = client
    client.eq.return_value = client
    client.execute = AsyncMock()
    return client


@pytest.fixture
def mock_form_schema():
    """Sample form schema for testing."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "employeeId": {"type": "string", "title": "รหัสพนักงาน"},
            "fullName": {"type": "string", "title": "ชื่อ-สกุล"},
            "equipments": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["Notebook", "Desktop Computer"]},
                        "quantity": {"type": "integer", "minimum": 1},
                    },
                },
            },
        },
        "required": ["employeeId", "fullName", "equipments"],
    }


@pytest.fixture
def sample_user_message():
    """Sample user message for testing."""
    return "I need 2 laptops for tomorrow morning"


@pytest.fixture
def sample_session_id():
    """Sample session ID for testing."""
    return "sess_test_12345"


@pytest.fixture
def sample_form_data():
    """Sample form data for testing."""
    return {
        "employeeId": "E12345",
        "fullName": "John Doe",
        "equipments": [{"type": "Notebook", "quantity": 2}],
    }
