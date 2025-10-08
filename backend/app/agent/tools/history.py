"""User history lookup tool for retrieving past form submissions."""
from typing import Any, Dict, List, Optional
from datetime import datetime


async def lookup_user_history(
    supabase_client: Any,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve user's previous form submissions from Supabase.
    
    Args:
        supabase_client: Supabase client instance
        session_id: Session ID to filter by (optional)
        user_id: User ID to filter by (optional)
        limit: Maximum number of submissions to retrieve (default: 5)
        
    Returns:
        List of form submissions, sorted by submitted_at descending (most recent first)
    """
    try:
        # Build the query
        query = supabase_client.table("form_submissions").select("*")
        
        # Apply filters
        if session_id:
            query = query.eq("session_id", session_id)
        if user_id:
            query = query.eq("user_id", user_id)
        
        # Order by most recent first and limit
        query = query.order("submitted_at", desc=True).limit(limit)
        
        # Execute the query
        response = await query.execute()
        
        # Return the data
        return response.data if response.data else []
        
    except Exception as e:
        # Log error in production
        print(f"Error retrieving user history: {e}")
        return []
