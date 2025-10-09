"""FastAPI main application.

This module implements the SiriForm Agent Chatbot API with two main endpoints:
1. POST /api/v1/chat - Process user messages and manage form state
2. GET /api/v1/form-schema/{form_name} - Retrieve form schemas
"""
import json
import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import ChatRequest, ChatResponse, FormSchemaResponse, HealthResponse
from app import __version__
from app.config import configure_langsmith
from app.routers import auth_router
from app.auth.dependencies import get_optional_user

# Configure LangSmith observability on startup
configure_langsmith()


# Initialize FastAPI app
app = FastAPI(
    title="SiriForm Agent Chatbot API",
    description="AI-powered conversational form filling assistant",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(auth_router)

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
async def chat(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Process a chat message and return agent response.
    
    This endpoint:
    1. Receives user message and current form state
    2. Uses the SiriAgent to process the message
    3. Saves chat history and form submissions to Supabase
    4. Returns updated form data and highlighted fields
    5. Maintains conversation context via session_id
    6. Optionally authenticates user via JWT token
    
    Args:
        request: ChatRequest containing message, session_id, and form_data
        current_user: Optional authenticated user from JWT token
        
    Returns:
        ChatResponse with agent's response, updated form_data, and metadata
    """
    try:
        # Extract user_id from auth token if available
        user_id = current_user["user_id"] if current_user else None
        
        # Log authentication status
        if user_id:
            print(f"✓ Authenticated user: {user_id} ({current_user.get('username')})")
        else:
            print("⚠ Anonymous user (no authentication)")
        
        # Import agent and clients
        from app.agent.SiriAgent import SiriAgent
        from app.llm import get_llm_client, get_supabase_client
        from app.services import SupabaseService
        
        # Get form schema (default to equipment_form)
        form_schema = load_form_schema("equipment_form")
        
        # Initialize clients
        llm = get_llm_client()
        
        # Try to get Supabase client, fall back to None if not configured
        supabase = None
        supabase_service = None
        try:
            supabase = get_supabase_client()
            supabase_service = SupabaseService(supabase)
        except ValueError:
            print("⚠ Supabase not configured - history and persistence disabled")
        
        # Save user message to chat history
        if supabase_service:
            message_data = {
                "session_id": request.session_id,
                "role": "user",
                "content": request.message
            }
            # Add user_id if authenticated
            if user_id:
                message_data["user_id"] = user_id
            supabase_service.save_message(**message_data)
        
        # Create SiriAgent instance
        agent = SiriAgent(
            llm=llm,
            supabase_client=supabase,
            form_schema=form_schema
        )
        
        # Process the message
        result = await agent.process_message(
            user_message=request.message,
            session_id=request.session_id,
            current_form_data=request.form_data
        )
        
        # Save assistant response to chat history
        if supabase_service:
            assistant_data = {
                "session_id": request.session_id,
                "role": "assistant",
                "content": result["response"],
                "confidence": result.get("confidence"),
                "highlighted_fields": result.get("highlighted_fields")
            }
            # Add user_id if authenticated
            if user_id:
                assistant_data["user_id"] = user_id
            supabase_service.save_message(**assistant_data)
            
            # Update or create form submission
            submission_data = {
                "session_id": request.session_id,
                "form_type": "equipment_form"
            }
            # Add user_id if authenticated
            if user_id:
                submission_data["user_id"] = user_id
                
            submission = supabase_service.get_or_create_submission(**submission_data)
            
            if submission:
                supabase_service.update_submission(
                    submission_id=submission["id"],
                    form_data=result["form_data"],
                    confidence_score=result.get("confidence")
                )
        
        return ChatResponse(**result)
        
    except Exception as e:
        # Log error and return fallback response
        print(f"❌ Error processing chat: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a simple fallback response
        return ChatResponse(
            response="ขออภัยครับ เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้งครับ",
            form_data=request.form_data or {},
            highlighted_fields=[],
            confidence=0.0
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
