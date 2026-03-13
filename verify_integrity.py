import os
import django
import sys

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_request_system.settings')
django.setup()

from access_requests.models import AccessRequest
from django.contrib.auth.models import User

def verify_id_generation():
    print("Starting verification of request_code generation...")
    
    # Clean up existing requests for this test (or specific ones)
    user, _ = User.objects.get_or_create(username='verify_user', defaults={'email': 'verify@test.com'})
    
    # 1. Create first request
    req1 = AccessRequest.objects.create(
        user=user, 
        firstname_en="Test1", 
        prefix="mr",
        reason="Test 1"
    )
    print(f"Created Req 1: {req1.request_code}")
    
    # 2. Create second request
    req2 = AccessRequest.objects.create(
        user=user, 
        firstname_en="Test2", 
        prefix="mr",
        reason="Test 2"
    )
    print(f"Created Req 2: {req2.request_code}")
    
    # 3. Simulate deletion (The cause of the bug)
    # Delete the FIRST one (req1) or middle one.
    # If we delete req1 (ID=1), count becomes 1.
    # Next create should be ID=3 (REQ-0003), but old logic (count+1) would try REQ-0002.
    # REQ-0002 already exists (req2). -> Crash.
    
    print(f"Deleting Req 1 ({req1.request_code})...")
    req1.delete()
    
    print(f"Current Count: {AccessRequest.objects.count()}")
    
    # 4. Create third request
    print("Attempting to create Req 3...")
    try:
        req3 = AccessRequest.objects.create(
            user=user, 
            firstname_en="Test3", 
            prefix="mr",
            reason="Test 3"
        )
        print(f"Created Req 3: {req3.request_code}")
    except Exception as e:
        print(f"FAILED: Created Req 3 failed with error: {e}")
        return

    # Check expectations
    # If req2 is REQ-0002, req3 should be REQ-0003.
    # If req3 is REQ-0002, it would have crashed (Unique Constraint).
    
    expected_code_suffix = int(req2.request_code.split('-')[1]) + 1
    actual_code_suffix = int(req3.request_code.split('-')[1])
    
    if actual_code_suffix == expected_code_suffix:
        print("SUCCESS: request_code generated correctly based on last ID.")
    else:
        print(f"WARNING: request_code {req3.request_code} was generated, but expected suffix {expected_code_suffix}")
    
    # Cleanup
    # req2.delete()
    # req3.delete()

if __name__ == '__main__':
    verify_id_generation()
