"""User history lookup tool for retrieving past form submissions."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def lookup_user_history(
    supabase_client: Any,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve user's previous form submissions from Supabase.
    
    This tool queries the form_submissions table to find historical data
    that can help the AI agent understand user patterns and preferences.
    
    Args:
        supabase_client: Supabase client instance (from get_supabase_client())
        session_id: Session ID to filter by (optional, recommended)
        user_id: User ID to filter by (optional, for authenticated users)
        limit: Maximum number of submissions to retrieve (default: 5, max: 20)
        
    Returns:
        List of form submission dictionaries containing:
        - id: Submission UUID
        - session_id: Session identifier
        - form_type: Type of form (e.g., 'equipment_form')
        - form_data: JSONB object with form fields
        - status: Submission status (draft, submitted, approved, rejected)
        - confidence_score: AI confidence score (0.00-1.00)
        - created_at: Creation timestamp
        - updated_at: Last update timestamp
        - submitted_at: Submission timestamp
        
    Example:
        >>> history = lookup_user_history(client, session_id="abc-123", limit=3)
        >>> if history:
        >>>     last_submission = history[0]
        >>>     print(f"Last request: {last_submission['form_data']}")
    """
    # Validate inputs
    if not supabase_client:
        logger.warning("Supabase client not available, skipping history lookup")
        return []
    
    if not session_id and not user_id:
        logger.warning("No session_id or user_id provided for history lookup")
        return []
    
    # Limit max results to prevent overload
    limit = min(limit, 20)
    
    try:
        # Build the query using Supabase Python client
        query = supabase_client.table("form_submissions").select("*")
        
        # Apply filters
        if session_id:
            query = query.eq("session_id", session_id)
        if user_id:
            query = query.eq("user_id", user_id)
        
        # Order by created_at (most recent first) and limit
        # Note: Use created_at instead of submitted_at to include drafts
        query = query.order("created_at", desc=True).limit(limit)
        
        # Execute the query (sync operation)
        response = query.execute()
        
        # Check response
        if hasattr(response, 'data') and response.data:
            logger.info(f"Retrieved {len(response.data)} historical submissions")
            return response.data
        else:
            logger.info("No historical submissions found")
            return []
        
    except AttributeError as e:
        # Supabase client method doesn't exist
        logger.error(f"Supabase client error (check client setup): {e}")
        return []
    except Exception as e:
        # General error handling
        logger.error(f"Error retrieving user history: {type(e).__name__}: {e}")
        return []


def get_recent_chat_history(
    supabase_client: Any,
    session_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Retrieve recent chat messages for a session.
    
    This can be used to provide conversation context to the agent
    if the conversation is resumed after a break.
    
    Args:
        supabase_client: Supabase client instance
        session_id: Session identifier
        limit: Maximum number of messages (default: 10, max: 50)
        
    Returns:
        List of chat message dictionaries containing:
        - id: Message UUID
        - session_id: Session identifier
        - role: Message role (user, assistant, system)
        - content: Message text content
        - confidence: AI confidence for this message
        - highlighted_fields: Array of field names updated
        - created_at: Message timestamp
    """
    if not supabase_client or not session_id:
        logger.warning("Cannot retrieve chat history: missing client or session_id")
        return []
    
    # Limit max results
    limit = min(limit, 50)
    
    try:
        query = supabase_client.table("chat_history").select("*")
        query = query.eq("session_id", session_id)
        query = query.order("created_at", desc=False).limit(limit)  # ASC for chronological order
        
        response = query.execute()
        
        if hasattr(response, 'data') and response.data:
            logger.info(f"Retrieved {len(response.data)} chat messages")
            return response.data
        else:
            return []
            
    except Exception as e:
        logger.error(f"Error retrieving chat history: {type(e).__name__}: {e}")
        return []


def save_chat_message(
    supabase_client: Any,
    session_id: str,
    role: str,
    content: str,
    submission_id: Optional[str] = None,
    confidence: Optional[float] = None,
    highlighted_fields: Optional[List[str]] = None
) -> bool:
    """
    Save a chat message to the database.
    
    Args:
        supabase_client: Supabase client instance
        session_id: Session identifier
        role: Message role ('user', 'assistant', 'system')
        content: Message content
        submission_id: Related form submission ID (optional)
        confidence: AI confidence score (optional)
        highlighted_fields: List of field names updated (optional)
        
    Returns:
        True if saved successfully, False otherwise
    """
    if not supabase_client or not session_id or not content:
        logger.warning("Cannot save chat message: missing required parameters")
        return False
    
    try:
        data = {
            "session_id": session_id,
            "role": role,
            "content": content,
        }
        
        if submission_id:
            data["submission_id"] = submission_id
        if confidence is not None:
            data["confidence"] = round(confidence, 2)
        if highlighted_fields:
            data["highlighted_fields"] = highlighted_fields
        
        response = supabase_client.table("chat_history").insert(data).execute()
        
        if hasattr(response, 'data') and response.data:
            logger.info(f"Saved {role} message to chat history")
            return True
        else:
            logger.warning("Failed to save chat message (no data returned)")
            return False
            
    except Exception as e:
        logger.error(f"Error saving chat message: {type(e).__name__}: {e}")
        return False
