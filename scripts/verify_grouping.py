
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
    print("\n--- Testing Incident Grouping ---")
    
    token = get_auth_token()
    if not token: return
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Send first event
    payload1 = {
        "source": "grouping_test_source",
        "event_type": "login_failed",
        "details": "First attempt",
        "severity": "medium",
        "data": {"fail_count": 5}
    }
    print(f"Sending Event 1: {payload1}")
    requests.post(f"{API_URL}/ingest/", json=payload1)
    time.sleep(2)

    # 2. Get the incident ID
    res = requests.get(f"{API_URL}/incidents/", headers=headers)
    if res.status_code != 200:
        print(f"❌ FAILURE: Failed to fetch incidents. Status: {res.status_code}, Response: {res.text}")
        return
    incidents = res.json()
    target_inc = None
    for inc in incidents:
        desc = inc.get("description") or ""
        if "Brute-force" in inc["title"] and "grouping_test_source" in desc:
            target_inc = inc
            break
    
    if not target_inc:
        print("❌ FAILURE: Initial incident not created.")
        return

    print(f"✅ Initial Incident Created: ID={target_inc['id']}, Alert Count={target_inc.get('alert_count', 'N/A')}")
    initial_id = target_inc['id']

    # 3. Send second event (SAME source & event_type)
    payload2 = {
        "source": "grouping_test_source",
        "event_type": "login_failed",
        "details": "Second attempt",
        "severity": "medium",
        "data": {"fail_count": 6}
    }
    print(f"Sending Event 2: {payload2}")
    requests.post(f"{API_URL}/ingest/", json=payload2)
    time.sleep(2)

    # 4. Check if merged
    res = requests.get(f"{API_URL}/incidents/{initial_id}", headers=headers)
    if res.status_code != 200:
        print("❌ FAILURE: Could not fetch incident.")
        return
    
    updated_inc = res.json()
    print(f"Updated Incident: Alert Count={updated_inc.get('alert_count', 'N/A')}")

    if updated_inc.get('alert_count') == 2: # Assuming start at 1 and +1
        print("✅ SUCCESS: Incident merged! Alert count increased.")
    elif updated_inc.get('alert_count') is None:
         print("⚠️ WARNING: alert_count field missing in response (check model/schema).")
    else:
        print(f"❌ FAILURE: Alert count did not increase as expected. Got {updated_inc.get('alert_count')}")

if __name__ == "__main__":
    test_incident_grouping()
