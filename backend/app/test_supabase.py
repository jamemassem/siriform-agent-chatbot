"""
Test script for Supabase integration.

This script tests:
1. Connection to Supabase
2. Creating form submissions
3. Saving chat history
4. Retrieving historical data
5. Updating submissions

Usage:
    cd backend
    uv run python -m app.test_supabase
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.llm import get_supabase_client
from app.services import SupabaseService
from app.agent.tools.history import lookup_user_history, get_recent_chat_history
from datetime import datetime


def test_connection():
    """Test 1: Verify Supabase connection."""
    print("\n" + "="*60)
    print("TEST 1: Supabase Connection")
    print("="*60)
    
    try:
        client = get_supabase_client()
        print("✓ Supabase client initialized successfully")
        return client
    except ValueError as e:
        print(f"✗ Failed to initialize Supabase client: {e}")
        print("\nPlease check:")
        print("1. .env file exists in backend/ directory")
        print("2. SUPABASE_URL and SUPABASE_KEY are set correctly")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


def test_create_submission(service: SupabaseService, session_id: str):
    """Test 2: Create a new form submission."""
    print("\n" + "="*60)
    print("TEST 2: Create Form Submission")
    print("="*60)
    
    try:
        submission = service.create_submission(
            session_id=session_id,
            form_type="equipment_form",
            form_data={
                "requester_name": "ทดสอบ ระบบ",
                "department": "IT",
                "purpose": "ทดสอบการเชื่อมต่อ Supabase"
            },
            status="draft",
            confidence_score=0.75
        )
        
        if submission:
            print(f"✓ Created submission with ID: {submission['id']}")
            print(f"  Session ID: {submission['session_id']}")
            print(f"  Status: {submission['status']}")
            print(f"  Confidence: {submission['confidence_score']}")
            return submission
        else:
            print("✗ Failed to create submission")
            return None
            
    except Exception as e:
        print(f"✗ Error creating submission: {e}")
        return None


def test_save_chat_messages(service: SupabaseService, session_id: str, submission_id: str):
    """Test 3: Save chat messages."""
    print("\n" + "="*60)
    print("TEST 3: Save Chat Messages")
    print("="*60)
    
    messages = [
        {
            "role": "user",
            "content": "ขอ laptop 2 เครื่องครับ"
        },
        {
            "role": "assistant",
            "content": "รับทราบครับ คุณต้องการใช้เมื่อไหร่ครับ?",
            "confidence": 0.85,
            "highlighted_fields": ["equipment_type", "quantity"]
        },
        {
            "role": "user",
            "content": "พรุ่งนี้เช้า 9 โมงครับ"
        },
        {
            "role": "assistant",
            "content": "เข้าใจแล้วครับ บันทึกเวลาเป็นพรุ่งนี้ 09:00 น. ใช้เพื่อวัตถุประสงค์อะไรครับ?",
            "confidence": 0.90,
            "highlighted_fields": ["pickup_date", "pickup_time"]
        }
    ]
    
    success_count = 0
    for msg in messages:
        try:
            result = service.save_message(
                session_id=session_id,
                submission_id=submission_id if msg["role"] == "assistant" else None,
                role=msg["role"],
                content=msg["content"],
                confidence=msg.get("confidence"),
                highlighted_fields=msg.get("highlighted_fields")
            )
            
            if result:
                print(f"✓ Saved {msg['role']} message")
                success_count += 1
            else:
                print(f"✗ Failed to save {msg['role']} message")
                
        except Exception as e:
            print(f"✗ Error saving {msg['role']} message: {e}")
    
    print(f"\nSaved {success_count}/{len(messages)} messages successfully")
    return success_count == len(messages)


def test_retrieve_history(client, session_id: str):
    """Test 4: Retrieve submission history."""
    print("\n" + "="*60)
    print("TEST 4: Retrieve Submission History")
    print("="*60)
    
    try:
        history = lookup_user_history(
            supabase_client=client,
            session_id=session_id,
            limit=5
        )
        
        if history:
            print(f"✓ Retrieved {len(history)} submission(s)")
            for i, item in enumerate(history, 1):
                print(f"\n  Submission {i}:")
                print(f"    ID: {item['id']}")
                print(f"    Status: {item['status']}")
                print(f"    Confidence: {item.get('confidence_score', 'N/A')}")
                print(f"    Created: {item['created_at']}")
                print(f"    Data: {item['form_data']}")
        else:
            print("✓ No history found (this is normal for first run)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error retrieving history: {e}")
        return False


def test_retrieve_chat_history(client, session_id: str):
    """Test 5: Retrieve chat history."""
    print("\n" + "="*60)
    print("TEST 5: Retrieve Chat History")
    print("="*60)
    
    try:
        history = get_recent_chat_history(
            supabase_client=client,
            session_id=session_id,
            limit=10
        )
        
        if history:
            print(f"✓ Retrieved {len(history)} message(s)")
            for i, msg in enumerate(history, 1):
                print(f"\n  Message {i}:")
                print(f"    Role: {msg['role']}")
                print(f"    Content: {msg['content'][:50]}...")
                if msg.get('confidence'):
                    print(f"    Confidence: {msg['confidence']}")
                if msg.get('highlighted_fields'):
                    print(f"    Highlighted: {msg['highlighted_fields']}")
        else:
            print("✓ No chat history found")
        
        return True
        
    except Exception as e:
        print(f"✗ Error retrieving chat history: {e}")
        return False


def test_update_submission(service: SupabaseService, submission_id: str):
    """Test 6: Update an existing submission."""
    print("\n" + "="*60)
    print("TEST 6: Update Submission")
    print("="*60)
    
    try:
        updated = service.update_submission(
            submission_id=submission_id,
            form_data={
                "requester_name": "ทดสอบ ระบบ",
                "department": "IT",
                "purpose": "ทดสอบการเชื่อมต่อ Supabase (อัปเดตแล้ว)",
                "equipment_type": "laptop",
                "quantity": 2,
                "pickup_date": "2025-10-10",
                "pickup_time": "09:00"
            },
            confidence_score=0.95,
            status="submitted",
            submitted_at=datetime.utcnow()
        )
        
        if updated:
            print(f"✓ Updated submission {submission_id}")
            print(f"  Status: {updated['status']}")
            print(f"  Confidence: {updated['confidence_score']}")
            print(f"  Submitted at: {updated.get('submitted_at', 'N/A')}")
            return True
        else:
            print("✗ Failed to update submission")
            return False
            
    except Exception as e:
        print(f"✗ Error updating submission: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SUPABASE INTEGRATION TEST")
    print("="*60)
    print("\nThis script will test Supabase database operations.")
    print("Make sure your .env file is configured correctly.\n")
    
    # Generate test session ID
    session_id = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    print(f"Test Session ID: {session_id}")
    
    # Test 1: Connection
    client = test_connection()
    if not client:
        print("\n❌ Cannot proceed without Supabase connection")
        return
    
    service = SupabaseService(client)
    
    # Test 2: Create submission
    submission = test_create_submission(service, session_id)
    if not submission:
        print("\n❌ Cannot proceed without submission")
        return
    
    submission_id = submission["id"]
    
    # Test 3: Save chat messages
    test_save_chat_messages(service, session_id, submission_id)
    
    # Test 4: Retrieve submission history
    test_retrieve_history(client, session_id)
    
    # Test 5: Retrieve chat history
    test_retrieve_chat_history(client, session_id)
    
    # Test 6: Update submission
    test_update_submission(service, submission_id)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("\n✓ All tests completed!")
    print(f"\nTest data created with session_id: {session_id}")
    print("\nYou can view this data in Supabase Dashboard:")
    print("1. Go to: https://app.supabase.com")
    print("2. Select your project")
    print("3. Go to 'Table Editor'")
    print("4. Check 'form_submissions' and 'chat_history' tables")
    print(f"5. Filter by session_id = '{session_id}'")


if __name__ == "__main__":
    main()
