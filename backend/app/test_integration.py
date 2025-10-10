"""
Integration Test Script for Frontend-Backend Connection

This script tests the full integration flow:
1. Backend health check
2. Get form schema
3. Send chat message (anonymous)
4. User registration
5. User login
6. Send chat message (authenticated)

Prerequisites:
- Backend running on http://localhost:8000
- Frontend running on http://localhost:5173

Usage:
    python -m app.test_integration
"""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": f"test_integration_{int(datetime.now().timestamp())}@example.com",
    "username": f"test_user_{int(datetime.now().timestamp())}",
    "password": "TestPassword123",
    "full_name": "Integration Test User"
}


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_success(text: str):
    """Print success message."""
    print(f"✅ {text}")


def print_error(text: str):
    """Print error message."""
    print(f"❌ {text}")


def print_info(text: str):
    """Print info message."""
    print(f"ℹ️  {text}")


async def test_health():
    """Test 1: Backend Health Check"""
    print_header("Test 1: Backend Health Check")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Backend is healthy!")
                print_info(f"Status: {data['status']}")
                print_info(f"Version: {data['version']}")
                return True
            else:
                print_error(f"Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Cannot connect to backend: {e}")
        print_info("Make sure backend is running: cd backend && uvicorn app.main:app --reload")
        return False


async def test_form_schema():
    """Test 2: Get Form Schema"""
    print_header("Test 2: Get Form Schema")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/form-schema/equipment_form")
            
            if response.status_code == 200:
                data = response.json()
                print_success("Form schema retrieved!")
                print_info(f"Form name: {data['name']}")
                print_info(f"Version: {data['version']}")
                print_info(f"Schema has {len(data['schema'].get('properties', {}))} properties")
                return data['schema']
            else:
                print_error(f"Failed to get schema: {response.status_code}")
                return None
    except Exception as e:
        print_error(f"Schema test failed: {e}")
        return None


async def test_chat_anonymous():
    """Test 3: Send Chat Message (Anonymous)"""
    print_header("Test 3: Chat Message (Anonymous)")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat",
                json={
                    "message": "ขอ laptop 2 เครื่อง สำหรับวันพรุ่งนี้",
                    "session_id": f"sess_test_anon_{int(datetime.now().timestamp())}",
                    "form_data": {}
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Anonymous chat works!")
                print_info(f"Response: {data['response'][:100]}...")
                print_info(f"Form data updated: {len(data.get('form_data', {}))} fields")
                print_info(f"Highlighted: {data.get('highlighted_fields', [])}")
                print_info(f"Confidence: {data.get('confidence', 'N/A')}")
                return data
            else:
                print_error(f"Chat failed: {response.status_code}")
                error = response.json()
                print_error(f"Detail: {error.get('detail', 'Unknown error')}")
                return None
    except Exception as e:
        print_error(f"Chat test failed: {e}")
        return None


async def test_register():
    """Test 4: User Registration"""
    print_header("Test 4: User Registration")
    
    try:
        async with httpx.AsyncClient() as client:
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
                print_info(f"Token: {data['access_token'][:20]}...")
                return data
            else:
                print_error(f"Registration failed: {response.status_code}")
                error = response.json()
                print_error(f"Detail: {error.get('detail', 'Unknown error')}")
                return None
    except Exception as e:
        print_error(f"Registration test failed: {e}")
        return None


async def test_login():
    """Test 5: User Login"""
    print_header("Test 5: User Login")
    
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
                print_info(f"Username: {data['username']}")
                print_info(f"Token: {data['access_token'][:20]}...")
                return data['access_token']
            else:
                print_error(f"Login failed: {response.status_code}")
                error = response.json()
                print_error(f"Detail: {error.get('detail', 'Unknown error')}")
                return None
    except Exception as e:
        print_error(f"Login test failed: {e}")
        return None


async def test_chat_authenticated(token: str):
    """Test 6: Send Chat Message (Authenticated)"""
    print_header("Test 6: Chat Message (Authenticated)")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "message": "ขอเม้าส์ 3 ตัว และ keyboard 2 ตัว",
                    "session_id": f"sess_test_auth_{int(datetime.now().timestamp())}",
                    "form_data": {}
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Authenticated chat works!")
                print_info(f"Response: {data['response'][:100]}...")
                print_info(f"Form data updated: {len(data.get('form_data', {}))} fields")
                print_info(f"Highlighted: {data.get('highlighted_fields', [])}")
                print_info(f"Confidence: {data.get('confidence', 'N/A')}")
                return data
            else:
                print_error(f"Chat failed: {response.status_code}")
                error = response.json()
                print_error(f"Detail: {error.get('detail', 'Unknown error')}")
                return None
    except Exception as e:
        print_error(f"Chat test failed: {e}")
        return None


async def test_get_profile(token: str):
    """Test 7: Get User Profile"""
    print_header("Test 7: Get User Profile")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Profile retrieved!")
                print_info(f"User ID: {data['user_id']}")
                print_info(f"Email: {data['email']}")
                print_info(f"Username: {data['username']}")
                print_info(f"Full Name: {data.get('full_name', 'N/A')}")
                return data
            else:
                print_error(f"Failed to get profile: {response.status_code}")
                return None
    except Exception as e:
        print_error(f"Profile test failed: {e}")
        return None


async def main():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("  🧪 FRONTEND-BACKEND INTEGRATION TEST")
    print("="*70)
    
    # Test 1: Health check
    if not await test_health():
        print_error("\n⚠️  Backend is not running. Stopping tests.")
        return
    
    # Test 2: Form schema
    schema = await test_form_schema()
    if not schema:
        print_error("\n⚠️  Form schema test failed. Stopping tests.")
        return
    
    # Test 3: Anonymous chat
    chat_result = await test_chat_anonymous()
    if not chat_result:
        print_error("\n⚠️  Anonymous chat test failed.")
    
    # Test 4: Registration
    reg_result = await test_register()
    if not reg_result:
        print_error("\n⚠️  Registration failed. Skipping auth tests.")
        return
    
    # Test 5: Login
    token = await test_login()
    if not token:
        print_error("\n⚠️  Login failed. Skipping remaining tests.")
        return
    
    # Test 6: Authenticated chat
    auth_chat = await test_chat_authenticated(token)
    if not auth_chat:
        print_error("\n⚠️  Authenticated chat test failed.")
    
    # Test 7: Get profile
    profile = await test_get_profile(token)
    
    # Summary
    print_header("Test Summary")
    print_success("All integration tests completed!")
    
    print_info("\n📝 Next steps:")
    print_info("1. Open http://localhost:5173 in browser")
    print_info("2. Test UI interactions:")
    print_info("   - Click 'เข้าสู่ระบบ' to open auth modal")
    print_info("   - Register or login with credentials")
    print_info("   - Send chat messages and watch form update")
    print_info("   - Verify highlighted fields animate")
    print_info("   - Check progress bar updates")
    print_info("3. Open browser DevTools (F12) to check:")
    print_info("   - Console for errors")
    print_info("   - Network tab for API calls")
    print_info("   - Application > Local Storage for auth token")
    print_info("4. Test logout and re-login flow")
    
    print("\n" + "="*70)
    print("  ✅ Integration Test Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
