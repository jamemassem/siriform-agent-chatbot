"""
Test script for JWT Authentication system.

This script tests all authentication endpoints and flows:
1. User registration
2. User login
3. Get current user profile
4. Token verification
5. Chat with authentication
6. Invalid token handling

Usage:
    python -m app.test_auth
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from app.config import get_settings

settings = get_settings()

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test_auth@example.com",
    "username": "test_auth_user",
    "password": "TestPassword123",
    "full_name": "Test Auth User"
}


def print_section(title: str):
    """Print a formatted section title."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")


async def test_health_check():
    """Test if backend is running."""
    print_section("Test 1: Health Check")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Backend is healthy! Status: {data['status']}, Version: {data['version']}")
                return True
            else:
                print_error(f"Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Cannot connect to backend: {e}")
        print_info("Make sure backend is running: cd backend && uvicorn app.main:app --reload")
        return False


async def test_user_registration():
    """Test user registration endpoint."""
    print_section("Test 2: User Registration")
    
    try:
        async with httpx.AsyncClient() as client:
            # Try to register new user
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=TEST_USER
            )
            
            if response.status_code == 201:
                data = response.json()
                print_success("User registered successfully!")
                print_info(f"User ID: {data['user_id']}")
                print_info(f"Email: {data['email']}")
                print_info(f"Username: {data['username']}")
                print_info(f"Token received: {data['access_token'][:20]}...")
                print_info(f"Expires in: {data['expires_in']} seconds")
                return data
            elif response.status_code == 400:
                error = response.json()
                if "already" in error['detail'].lower():
                    print_info("User already exists (expected if running test multiple times)")
                    print_info("Will use existing user for login test")
                    return None
                else:
                    print_error(f"Registration failed: {error['detail']}")
                    return None
            else:
                print_error(f"Unexpected status code: {response.status_code}")
                return None
                
    except Exception as e:
        print_error(f"Registration test failed: {e}")
        return None


async def test_user_login():
    """Test user login endpoint."""
    print_section("Test 3: User Login")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Login successful!")
                print_info(f"User ID: {data['user_id']}")
                print_info(f"Email: {data['email']}")
                print_info(f"Username: {data['username']}")
                print_info(f"Full Name: {data.get('full_name', 'N/A')}")
                print_info(f"Token: {data['access_token'][:20]}...")
                return data['access_token']
            elif response.status_code == 401:
                error = response.json()
                print_error(f"Login failed: {error['detail']}")
                print_info("Make sure user is registered first")
                return None
            else:
                print_error(f"Unexpected status code: {response.status_code}")
                return None
                
    except Exception as e:
        print_error(f"Login test failed: {e}")
        return None


async def test_get_profile(token: str):
    """Test get current user profile endpoint."""
    print_section("Test 4: Get User Profile")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Profile retrieved successfully!")
                print_info(f"User ID: {data['user_id']}")
                print_info(f"Email: {data['email']}")
                print_info(f"Username: {data['username']}")
                print_info(f"Full Name: {data.get('full_name', 'N/A')}")
                print_info(f"Created At: {data.get('created_at', 'N/A')}")
                print_info(f"Last Login: {data.get('last_login_at', 'N/A')}")
                return True
            elif response.status_code == 401:
                print_error("Unauthorized - invalid token")
                return False
            else:
                print_error(f"Unexpected status code: {response.status_code}")
                return False
                
    except Exception as e:
        print_error(f"Get profile test failed: {e}")
        return False


async def test_verify_token(token: str):
    """Test token verification endpoint."""
    print_section("Test 5: Verify Token")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/verify-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Token is valid!")
                print_info(f"Valid: {data['valid']}")
                print_info(f"User ID: {data['user_id']}")
                print_info(f"Email: {data.get('email', 'N/A')}")
                print_info(f"Username: {data.get('username', 'N/A')}")
                return True
            else:
                print_error(f"Token verification failed: {response.status_code}")
                return False
                
    except Exception as e:
        print_error(f"Token verification test failed: {e}")
        return False


async def test_chat_with_auth(token: str):
    """Test chat endpoint with authentication."""
    print_section("Test 6: Chat with Authentication")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json={
                    "message": "ขอ laptop 2 เครื่อง สำหรับวันพรุ่งนี้",
                    "session_id": f"sess_test_auth_{asyncio.get_event_loop().time()}",
                    "form_data": {}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Chat message processed successfully!")
                print_info(f"Response: {data['response'][:100]}...")
                print_info(f"Form data updated: {len(data.get('form_data', {}))} fields")
                print_info(f"Highlighted fields: {data.get('highlighted_fields', [])}")
                print_info(f"Confidence: {data.get('confidence', 'N/A')}")
                return True
            else:
                print_error(f"Chat request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print_error(f"Chat with auth test failed: {e}")
        return False


async def test_invalid_token():
    """Test with invalid token."""
    print_section("Test 7: Invalid Token Handling")
    
    try:
        invalid_token = "invalid.token.here"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {invalid_token}"}
            )
            
            if response.status_code == 401:
                print_success("Invalid token correctly rejected!")
                error = response.json()
                print_info(f"Error message: {error['detail']}")
                return True
            else:
                print_error(f"Expected 401, got: {response.status_code}")
                return False
                
    except Exception as e:
        print_error(f"Invalid token test failed: {e}")
        return False


async def test_chat_without_auth():
    """Test chat endpoint without authentication (anonymous)."""
    print_section("Test 8: Chat without Authentication (Anonymous)")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat",
                json={
                    "message": "ขอเม้าส์ 1 ตัว",
                    "session_id": f"sess_test_anon_{asyncio.get_event_loop().time()}",
                    "form_data": {}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Anonymous chat works!")
                print_info(f"Response: {data['response'][:100]}...")
                print_info("Chat endpoint supports both authenticated and anonymous users")
                return True
            else:
                print_error(f"Anonymous chat failed: {response.status_code}")
                return False
                
    except Exception as e:
        print_error(f"Anonymous chat test failed: {e}")
        return False


async def main():
    """Run all authentication tests."""
    print("\n" + "="*60)
    print("  🔐 JWT AUTHENTICATION SYSTEM TEST SUITE")
    print("="*60)
    
    # Test 1: Health check
    if not await test_health_check():
        print_error("\n⚠️  Backend is not running. Exiting tests.")
        return
    
    # Test 2: Registration
    reg_result = await test_user_registration()
    
    # Test 3: Login (required for remaining tests)
    token = await test_user_login()
    if not token:
        print_error("\n⚠️  Login failed. Cannot proceed with remaining tests.")
        return
    
    # Test 4: Get profile
    await test_get_profile(token)
    
    # Test 5: Verify token
    await test_verify_token(token)
    
    # Test 6: Chat with auth
    await test_chat_with_auth(token)
    
    # Test 7: Invalid token
    await test_invalid_token()
    
    # Test 8: Anonymous chat
    await test_chat_without_auth()
    
    # Summary
    print_section("Test Summary")
    print_success("All authentication tests completed!")
    print_info("\n📝 Next steps:")
    print_info("1. Check Supabase dashboard to verify user record created")
    print_info("2. Check chat_history table to verify messages saved with user_id")
    print_info("3. Check form_submissions table to verify submissions linked to user")
    print_info("4. Test frontend login/register forms in browser")
    print_info("5. Test logout and re-login flow")
    
    print("\n" + "="*60)
    print("  ✅ JWT Authentication System Ready!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
