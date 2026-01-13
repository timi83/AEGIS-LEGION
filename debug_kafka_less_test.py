import requests
import json
import base64

import random
import string

# Configuration
API_URL = "http://localhost:8000/api"
rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
TEST_EMAIL = f"test_verifier_{rand_suffix}@gmail.com"
LOGIN_DATA = {"username": TEST_EMAIL, "password": "password123"}
EVENT_DATA = {
    "source": "verification-script",
    "event_type": "verification_test_event",
    "severity": "medium",
    "details": "Checking if rule engine works without Kafka",
    "data": {"foo": "bar"}
}

def run_test():
    print(f"🚀 Testing Registration Only (Fix Verification)...")
    
    # New random suffix for this run
    rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"debug_502_{rand_suffix}@test.com"
    
    print(f"📝 Attempting to register {test_email}...")
    try:
        reg_res = requests.post(f"{API_URL}/register", json={
            "username": f"debug_user_{rand_suffix}",
            "email": test_email, 
            "password": "password123", 
            "full_name": "Debug 502 User",
            "organization": f"DebugOrg_{rand_suffix}"
        })
        print(f"   Response Code: {reg_res.status_code}")
        print(f"   Response Body: {reg_res.text}")
    except Exception as e:
        print(f"   Request Failed: {e}")
    
    print("🔑 Authenticating...")
    login_res = requests.post(f"{API_URL}/token", data={"username": test_email, "password": "password123"})
    if login_res.status_code != 200:
        print(f"❌ Login Failed: {login_res.text}")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Send Event to Ingest
    print("📤 Sending Event to /api/ingest/...")
    # Note: Ensure EVENT_DATA is defined or re-define it here
    event_payload = {
        "source": "verification-script",
        "event_type": "malware_detected",
        "severity": "high",
        "details": "Checking critical rule fallback",
        "data": {"foo": "bar"}
    }
    
    res = requests.post(f"{API_URL}/ingest/", json=event_payload, headers=headers)
    
    if res.status_code == 200:
        print(f"✅ SUCCESS: Ingest API returned 200 OK")
        print(f"   Response: {res.json()}")
    else:
        print(f"❌ FAILED: Ingest API returned {res.status_code}")
        print(f"   Body: {res.text}")

if __name__ == "__main__":
    run_test()
