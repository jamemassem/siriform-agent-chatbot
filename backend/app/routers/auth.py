"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models import Token, UserLogin, UserRegister, UserResponse
from app.services.auth_service import get_auth_service, AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password.",
)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Register a new user account.

    Returns:
        - **user_id**: Unique user identifier
        - **email**: User's email
        - **username**: User's username
        - **access_token**: JWT token for authentication
        - **token_type**: Token type (bearer)
        - **expires_in**: Token expiration time in seconds
    """
    try:
        result = await auth_service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post(
    "/login",
    response_model=dict,
    summary="Login user",
    description="Authenticate user with username/email and password to get JWT token.",
)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Authenticate user and generate JWT access token.

    Returns:
        - **user_id**: Unique user identifier
        - **email**: User's email
        - **username**: User's username
        - **access_token**: JWT token for authentication
        - **token_type**: Token type (bearer)
        - **expires_in**: Token expiration time in seconds
    """
    try:
        result = await auth_service.login_user(
            username=credentials.username,
            password=credentials.password,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get the profile information of the currently authenticated user.",
)
async def get_me(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get current authenticated user's profile.

    Requires:
        - Valid JWT token in Authorization header

    Returns:
        User profile information including user_id, email, username, full_name, etc.
    """
    try:
        user_id = current_user["user_id"]
        profile = await auth_service.get_user_profile(user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}",
        )


@router.post(
    "/verify-token",
    response_model=dict,
    summary="Verify JWT token",
    description="Verify if the provided JWT token is valid and return user info.",
)
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify JWT token validity.

    Requires:
        - Valid JWT token in Authorization header

    Returns:
        Dictionary with user information from the token (user_id, email, username)
    """
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "email": current_user.get("email"),
        "username": current_user.get("username"),
    }
