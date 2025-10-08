"""FastAPI main application.

This module implements the SiriForm Agent Chatbot API with two main endpoints:
1. POST /api/v1/chat - Process user messages and manage form state
2. GET /api/v1/form-schema/{form_name} - Retrieve form schemas
"""
import json
import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import ChatRequest, ChatResponse, FormSchemaResponse, HealthResponse
from app import __version__


# Initialize FastAPI app
app = FastAPI(
    title="SiriForm Agent Chatbot API",
    description="AI-powered conversational form filling assistant",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",   # Alternative dev port
        # Add production origins here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_form_schema(form_name: str) -> Dict[str, Any]:
    """Load a form schema from the schemas directory.
    
    Args:
        form_name: Name of the form (without .json extension)
        
    Returns:
        Parsed JSON schema dictionary
        
    Raises:
        HTTPException: If schema file not found
    """
    schema_path = Path(__file__).parent / "schemas" / f"{form_name}.json"
    
    if not schema_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Form schema '{form_name}' not found"
        )
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=__version__)


@app.get("/api/v1/form-schema/{form_name}", response_model=FormSchemaResponse)
async def get_form_schema(form_name: str):
    """Retrieve a form schema by name.
    
    Args:
        form_name: Name of the form (e.g., 'equipment_form')
        
    Returns:
        FormSchemaResponse containing name, version, and schema
    """
    schema = load_form_schema(form_name)
    
    return FormSchemaResponse(
        name=form_name,
        version=schema.get("version", "1.0.0"),
        schema=schema
    )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return agent response.
    
    This endpoint:
    1. Receives user message and current form state
    2. Uses the SiriAgent to process the message
    3. Returns updated form data and highlighted fields
    4. Maintains conversation context via session_id
    
    Args:
        request: ChatRequest containing message, session_id, and form_data
        
    Returns:
        ChatResponse with agent's response, updated form_data, and metadata
    """
    # TODO: Implement SiriAgent integration (T015)
    # For now, return a stub response to pass contract tests
    
    # Extract basic information from the message
    message = request.message.lower()
    form_data = request.form_data.copy() if request.form_data else {}
    highlighted_fields = []
    
    # Simple pattern matching for demonstration
    if "laptop" in message or "notebook" in message:
        if "equipments" not in form_data:
            form_data["equipments"] = []
        
        # Extract quantity if mentioned
        import re
        qty_match = re.search(r'(\d+)', message)
        quantity = int(qty_match.group(1)) if qty_match else 1
        
        form_data["equipments"].append({
            "type": "Notebook",
            "quantity": quantity,
            "detail": ""
        })
        highlighted_fields.append("equipments")
        response_text = f"เข้าใจแล้วครับ คุณต้องการ Notebook จำนวน {quantity} เครื่อง"
        confidence = 0.9
    else:
        response_text = "ขอบคุณครับ คุณต้องการอุปกรณ์อะไรบ้างครับ?"
        confidence = 0.5
    
    return ChatResponse(
        response=response_text,
        form_data=form_data,
        highlighted_fields=highlighted_fields,
        confidence=confidence
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
