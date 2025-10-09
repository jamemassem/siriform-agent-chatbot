"""
Authentication module for SiriForm Agent Chatbot.

This module provides JWT-based authentication including:
- Password hashing and verification
- JWT token generation and validation
- User authentication utilities
"""

from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from .dependencies import get_current_user, get_optional_user

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_optional_user",
]
