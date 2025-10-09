"""
Supabase service for managing form submissions and chat history.

This module provides high-level functions for interacting with Supabase
database tables: form_submissions, chat_history, and user_sessions.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service class for Supabase database operations."""
    
    def __init__(self, supabase_client: Any):
        """
        Initialize Supabase service.
        
        Args:
            supabase_client: Initialized Supabase client from get_supabase_client()
        """
        self.client = supabase_client
    
    # ==================== Form Submissions ====================
    
    def create_submission(
        self,
        session_id: str,
        form_type: str = "equipment_form",
        form_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        status: str = "draft",
        confidence_score: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new form submission.
        
        Args:
            session_id: Session identifier
            form_type: Type of form (default: 'equipment_form')
            form_data: Form field data (JSONB)
            user_id: User ID for authenticated users
            status: Submission status (draft, submitted, approved, rejected)
            confidence_score: AI confidence (0.00-1.00)
            
        Returns:
            Created submission dict with ID, or None if failed
        """
        try:
            data = {
                "session_id": session_id,
                "form_type": form_type,
                "form_data": form_data or {},
                "status": status,
            }
            
            if user_id:
                data["user_id"] = user_id
            if confidence_score is not None:
                data["confidence_score"] = round(confidence_score, 2)
            
            response = self.client.table("form_submissions").insert(data).execute()
            
            if hasattr(response, 'data') and response.data:
                logger.info(f"Created form submission: {response.data[0]['id']}")
                return response.data[0]
            else:
                logger.warning("Failed to create submission (no data returned)")
                return None
                
        except Exception as e:
            logger.error(f"Error creating submission: {type(e).__name__}: {e}")
            return None
    
    def update_submission(
        self,
        submission_id: str,
        form_data: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        confidence_score: Optional[float] = None,
        submitted_at: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing form submission.
        
        Args:
            submission_id: UUID of submission to update
            form_data: Updated form data (will merge with existing)
            status: New status
            confidence_score: Updated confidence
            submitted_at: Submission timestamp (set when status='submitted')
            
        Returns:
            Updated submission dict, or None if failed
        """
        try:
            data = {}
            
            if form_data is not None:
                data["form_data"] = form_data
            if status:
                data["status"] = status
            if confidence_score is not None:
                data["confidence_score"] = round(confidence_score, 2)
            if submitted_at:
                data["submitted_at"] = submitted_at.isoformat()
            
            if not data:
                logger.warning("No data provided for update")
                return None
            
            response = (
                self.client.table("form_submissions")
                .update(data)
                .eq("id", submission_id)
                .execute()
            )
            
            if hasattr(response, 'data') and response.data:
                logger.info(f"Updated submission: {submission_id}")
                return response.data[0]
            else:
                logger.warning(f"Failed to update submission {submission_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating submission: {type(e).__name__}: {e}")
            return None
    
    def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific form submission by ID.
        
        Args:
            submission_id: UUID of submission
            
        Returns:
            Submission dict, or None if not found
        """
        try:
            response = (
                self.client.table("form_submissions")
                .select("*")
                .eq("id", submission_id)
                .execute()
            )
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving submission: {type(e).__name__}: {e}")
            return None
    
    def get_session_submissions(
        self,
        session_id: str,
        limit: int = 10,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all submissions for a session.
        
        Args:
            session_id: Session identifier
            limit: Max number of results (default: 10)
            status_filter: Filter by status (optional)
            
        Returns:
            List of submission dicts, sorted by created_at DESC
        """
        try:
            query = self.client.table("form_submissions").select("*")
            query = query.eq("session_id", session_id)
            
            if status_filter:
                query = query.eq("status", status_filter)
            
            query = query.order("created_at", desc=True).limit(limit)
            response = query.execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving submissions: {type(e).__name__}: {e}")
            return []
    
    def get_or_create_submission(
        self,
        session_id: str,
        form_type: str = "equipment_form",
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest draft submission for a session, or create new if none exists.
        
        This is useful for maintaining a single active form per session.
        
        Args:
            session_id: Session identifier
            form_type: Form type to look for
            user_id: Optional user ID for authenticated users
            
        Returns:
            Submission dict (existing or new)
        """
        # Try to get existing draft
        existing = self.get_session_submissions(
            session_id=session_id,
            limit=1,
            status_filter="draft"
        )
        
        if existing:
            logger.info(f"Found existing draft submission: {existing[0]['id']}")
            return existing[0]
        
        # Create new submission
        logger.info("No draft found, creating new submission")
        create_data = {
            "session_id": session_id,
            "form_type": form_type,
            "status": "draft"
        }
        if user_id:
            create_data["user_id"] = user_id
            
        return self.create_submission(**create_data)
    
    # ==================== Chat History ====================
    
    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        submission_id: Optional[str] = None,
        confidence: Optional[float] = None,
        highlighted_fields: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Save a chat message to history.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message text
            submission_id: Related submission UUID
            confidence: AI confidence score
            highlighted_fields: List of updated field names
            user_id: User ID for authenticated users
            
        Returns:
            True if saved successfully
        """
        try:
            data = {
                "session_id": session_id,
                "role": role,
                "content": content,
            }
            
            if user_id:
                data["user_id"] = user_id
            if submission_id:
                data["submission_id"] = submission_id
            if confidence is not None:
                data["confidence"] = round(confidence, 2)
            if highlighted_fields:
                data["highlighted_fields"] = highlighted_fields
            
            response = self.client.table("chat_history").insert(data).execute()
            
            if hasattr(response, 'data') and response.data:
                logger.info(f"Saved {role} message to history")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error saving message: {type(e).__name__}: {e}")
            return False
    
    def get_chat_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chat history for a session.
        
        Args:
            session_id: Session identifier
            limit: Max messages to retrieve (default: 50)
            
        Returns:
            List of message dicts, sorted chronologically (ASC)
        """
        try:
            query = self.client.table("chat_history").select("*")
            query = query.eq("session_id", session_id)
            query = query.order("created_at", desc=False).limit(limit)
            
            response = query.execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving chat history: {type(e).__name__}: {e}")
            return []
    
    # ==================== User Sessions ====================
    
    def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new user session record.
        
        Args:
            session_id: Unique session identifier
            user_id: User ID (if authenticated)
            ip_address: Client IP address
            user_agent: Browser user agent string
            
        Returns:
            Created session dict, or None if failed
        """
        try:
            data = {"session_id": session_id}
            
            if user_id:
                data["user_id"] = user_id
            if ip_address:
                data["ip_address"] = ip_address
            if user_agent:
                data["user_agent"] = user_agent
            
            response = self.client.table("user_sessions").insert(data).execute()
            
            if hasattr(response, 'data') and response.data:
                logger.info(f"Created session record: {session_id}")
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error creating session: {type(e).__name__}: {e}")
            return None
    
    def update_session_activity(self, session_id: str) -> bool:
        """
        Update last_activity timestamp for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if updated successfully
        """
        try:
            response = (
                self.client.table("user_sessions")
                .update({"last_activity": datetime.utcnow().isoformat()})
                .eq("session_id", session_id)
                .execute()
            )
            
            if hasattr(response, 'data') and response.data:
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error updating session activity: {type(e).__name__}: {e}")
            return False
