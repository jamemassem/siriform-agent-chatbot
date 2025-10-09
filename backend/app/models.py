"""Pydantic models for API request and response bodies."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., description="User's chat message")
    session_id: str = Field(..., description="Session identifier for conversation tracking")
    form_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Current form data state"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "I need 2 laptops for tomorrow",
                    "session_id": "sess_abc123",
                    "form_data": {},
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="Agent's response message")
    form_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Updated form data"
    )
    highlighted_fields: List[str] = Field(
        default_factory=list,
        description="List of field names that were updated by the agent",
    )
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Confidence score of the agent's response"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response": "ได้ค่ะ คุณต้องการยืมโน้ตบุ๊ก 2 เครื่องสำหรับวันพรุ่งนี้ใช่ไหมคะ?",
                    "form_data": {"equipments": [{"type": "Notebook", "quantity": 2}]},
                    "highlighted_fields": ["equipments"],
                    "confidence": 0.95,
                }
            ]
        }
    }


class FormSchemaResponse(BaseModel):
    """Response model for form schema endpoint."""

    name: str = Field(..., description="Form name")
    version: str = Field(..., description="Schema version")
    schema: Dict[str, Any] = Field(..., description="JSON schema definition")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "equipment_form",
                    "version": "1.0.0",
                    "schema": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "properties": {},
                    },
                }
            ]
        }
    }


class Equipment(BaseModel):
    """Equipment item model."""

    type: str = Field(..., description="Equipment type")
    quantity: int = Field(..., ge=1, le=50, description="Quantity")
    detail: Optional[str] = Field(default=None, description="Equipment details")


class FormSubmission(BaseModel):
    """Form submission model matching database schema."""

    id: Optional[str] = Field(default=None, description="Submission ID")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    form_schema_id: str = Field(..., description="Form schema ID")
    submitted_at: Optional[str] = Field(default=None, description="Submission timestamp")
    data: Dict[str, Any] = Field(..., description="Form data")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "user_123",
                    "session_id": "sess_abc",
                    "form_schema_id": "equipment_form_v1",
                    "data": {
                        "employeeId": "E12345",
                        "fullName": "สมชาย ใจดี",
                        "equipments": [{"type": "Notebook", "quantity": 2}],
                    },
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")

    model_config = {"json_schema_extra": {"examples": [{"status": "healthy", "version": "0.1.0"}]}}


# Authentication Models

class UserRegister(BaseModel):
    """User registration request model."""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(default=None, description="User's full name")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "username": "john_doe",
                    "password": "securePassword123",
                    "full_name": "John Doe",
                }
            ]
        }
    }


class UserLogin(BaseModel):
    """User login request model."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

    model_config = {
        "json_schema_extra": {
            "examples": [{"username": "john_doe", "password": "securePassword123"}]
        }
    }


class Token(BaseModel):
    """JWT token response model."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"access_token": "eyJhbGc...", "token_type": "bearer", "expires_in": 86400}
            ]
        }
    }


class UserResponse(BaseModel):
    """User profile response model."""

    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(default=None, description="Full name")
    created_at: Optional[str] = Field(default=None, description="Account creation timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "user_123",
                    "email": "user@example.com",
                    "username": "john_doe",
                    "full_name": "John Doe",
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ]
        }
    }
