"""
Authentication service for user registration and login.
"""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from app.auth.security import create_access_token, get_password_hash, verify_password
from app.config import get_settings
from app.services.supabase_service import get_supabase_client

settings = get_settings()


class AuthService:
    """Service for user authentication operations."""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def register_user(
        self, email: str, username: str, password: str, full_name: Optional[str] = None
    ) -> dict:
        """
        Register a new user.

        Args:
            email: User's email address
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: Optional full name

        Returns:
            Dictionary with user data and access token

        Raises:
            ValueError: If user already exists or registration fails
        """
        if not self.supabase:
            raise ValueError("Supabase client not configured")

        # Check if email already exists
        existing_email = (
            self.supabase.table("users").select("id").eq("email", email).execute()
        )
        if existing_email.data:
            raise ValueError("Email already registered")

        # Check if username already exists
        existing_username = (
            self.supabase.table("users").select("id").eq("username", username).execute()
        )
        if existing_username.data:
            raise ValueError("Username already taken")

        # Hash password
        password_hash = get_password_hash(password)

        # Create user
        user_data = {
            "email": email,
            "username": username,
            "password_hash": password_hash,
            "full_name": full_name,
            "is_active": True,
            "is_verified": False,
        }

        result = self.supabase.table("users").insert(user_data).execute()

        if not result.data:
            raise ValueError("Failed to create user")

        user = result.data[0]

        # Generate access token
        access_token = create_access_token(
            data={
                "sub": str(user["id"]),
                "email": user["email"],
                "username": user["username"],
            },
            expires_delta=timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        )

        return {
            "user_id": str(user["id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        }

    async def login_user(self, username: str, password: str) -> dict:
        """
        Authenticate a user and generate access token.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            Dictionary with user data and access token

        Raises:
            ValueError: If credentials are invalid
        """
        if not self.supabase:
            raise ValueError("Supabase client not configured")

        # Try to find user by username or email
        user_result = (
            self.supabase.table("users")
            .select("*")
            .or_(f"username.eq.{username},email.eq.{username}")
            .eq("is_active", True)
            .execute()
        )

        if not user_result.data:
            raise ValueError("Invalid username or password")

        user = user_result.data[0]

        # Verify password
        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid username or password")

        # Update last login timestamp
        self.supabase.rpc("update_user_last_login", {"user_id": user["id"]}).execute()

        # Generate access token
        access_token = create_access_token(
            data={
                "sub": str(user["id"]),
                "email": user["email"],
                "username": user["username"],
            },
            expires_delta=timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        )

        return {
            "user_id": str(user["id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        }

    async def get_user_profile(self, user_id: str) -> Optional[dict]:
        """
        Get user profile by user ID.

        Args:
            user_id: User UUID

        Returns:
            User profile data or None if not found
        """
        if not self.supabase:
            return None

        result = (
            self.supabase.table("users")
            .select("id, email, username, full_name, created_at, last_login_at")
            .eq("id", user_id)
            .eq("is_active", True)
            .execute()
        )

        if not result.data:
            return None

        user = result.data[0]
        return {
            "user_id": str(user["id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "created_at": user.get("created_at"),
            "last_login_at": user.get("last_login_at"),
        }


def get_auth_service() -> AuthService:
    """Get AuthService instance."""
    return AuthService()
