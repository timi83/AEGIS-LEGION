
import sys
import os
import requests
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

API_URL = "http://127.0.0.1:8000/api"

def get_auth_token():
    # Register/Login to get token
    username = f"testuser_{int(time.time())}"
    password = "password123"
    
    # Register
    requests.post(f"{API_URL}/register", json={"username": username, "password": password})
    
    # Login
    res = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    print("❌ Failed to get auth token")
    return None

def test_incident_grouping():
    print("\n--- Testing Incident Grouping (Robust) ---")
    
    token = get_auth_token()
    if not token: return
    headers = {"Authorization": f"Bearer {token}"}

    source = "grouping_test_source_robust"
    
    # 1. Send first event
    payload1 = {
        "source": source,
        "event_type": "login_failed",
        "details": "First attempt",
        "severity": "medium",
        "data": {"fail_count": 5}
    }
    print(f"Sending Event 1: {payload1}")
    requests.post(f"{API_URL}/ingest/", json=payload1)
    
    # Poll for creation
    print("Waiting for initial incident...")
    initial_inc = None
    for i in range(10):
        time.sleep(1)
        res = requests.get(f"{API_URL}/incidents/", headers=headers)
        if res.status_code == 200:
            for inc in res.json():
                desc = inc.get("description") or ""
                if "Brute-force" in inc["title"] and source in desc:
                    initial_inc = inc
                    break
        if initial_inc: break
    
    if not initial_inc:
        print("❌ FAILURE: Initial incident not created after 10s.")
        return

    print(f"✅ Initial Incident Created: ID={initial_inc['id']}, Alert Count={initial_inc.get('alert_count', 'N/A')}")
    
    # 2. Send second event
    payload2 = {
        "source": source,
        "event_type": "login_failed",
        "details": "Second attempt",
        "severity": "medium",
        "data": {"fail_count": 6}
    }
    print(f"Sending Event 2: {payload2}")
    requests.post(f"{API_URL}/ingest/", json=payload2)
    
    # Poll for update
    print("Waiting for update...")
    updated = False
    for i in range(10):
        time.sleep(1)
        res = requests.get(f"{API_URL}/incidents/{initial_inc['id']}", headers=headers)
        if res.status_code == 200:
            inc = res.json()
            count = inc.get("alert_count")
            print(f"  Poll {i+1}: Alert Count = {count}")
            if count and count >= 2:
                updated = True
                break
    
    if updated:
        print("✅ SUCCESS: Incident merged! Alert count increased.")
    else:
        print("❌ FAILURE: Alert count did not increase after 10s.")
        # Check if a NEW incident was created instead
        res = requests.get(f"{API_URL}/incidents/", headers=headers)
        if res.status_code == 200:
            count_for_source = 0
            for inc in res.json():
                desc = inc.get("description") or ""
                if source in desc:
                    count_for_source += 1
            print(f"ℹ️ Total incidents for source '{source}': {count_for_source}")

if __name__ == "__main__":
    test_incident_grouping()
