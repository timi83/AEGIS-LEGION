# scripts/verify_step7.py
import requests
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend'))
from src.services.notification_service import get_env_vars

# Load env to get token if needed, but for now assuming no auth or using a test token
# For simplicity, we'll just try to hit the endpoints. If auth is required, we might need to login first.
# The previous scripts showed we might need a token.

BASE_URL = "http://127.0.0.1:8000/api"

def login():
    # 1. Try to register first (ignore if exists)
    try:
        # Endpoint is /api/register
        reg_resp = requests.post(f"{BASE_URL}/register", json={"username": "verify_user", "password": "verify_password"})
        if reg_resp.status_code != 200 and reg_resp.status_code != 400: # 400 means already exists
             print(f"Registration warning: {reg_resp.status_code} {reg_resp.text}")
    except Exception as e:
        print(f"Registration error: {e}")

    try:
        # 2. Login
        resp = requests.post(f"{BASE_URL}/token", data={"username": "verify_user", "password": "verify_password"})
        if resp.status_code == 200:
            return resp.json()["access_token"]
        print(f"Login failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Login error: {e}")
    return None

def verify():
    token = login()
    if not token:
        print("❌ Could not get auth token. Skipping verification.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get an existing incident or create one
    print("1. Fetching incidents...")
    resp = requests.get(f"{BASE_URL}/incidents/", headers=headers)
    incidents = resp.json()
    
    if not incidents:
        print("⚠️ No incidents found. Creating a test incident...")
        # Create a manual incident via ingest if needed, or just skip
        # Let's try to use the ingest API to create one
        requests.post(f"{BASE_URL}/ingest/", json={
            "event_type": "step7_test",
            "severity": "low",
            "source": "verification_script",
            "data": {"note": "test"}
        })
        # Fetch again
        resp = requests.get(f"{BASE_URL}/incidents/", headers=headers)
        incidents = resp.json()

    if not incidents:
        print("❌ Still no incidents. Cannot verify.")
        return

    incident_id = incidents[0]["id"]
    print(f"✅ Using Incident ID: {incident_id}")

    # 2. Update Status
    print(f"2. Updating status of Incident {incident_id} to 'investigating'...")
    resp = requests.put(f"{BASE_URL}/incidents/{incident_id}/update-status?new_status=investigating", headers=headers)
    if resp.status_code == 200:
        print("✅ Status update successful.")
    else:
        print(f"❌ Status update failed: {resp.status_code} {resp.text}")

    # 3. Add Note
    print(f"3. Adding response note to Incident {incident_id}...")
    resp = requests.put(f"{BASE_URL}/incidents/{incident_id}/add-note?note=Verification Script Note", headers=headers)
    if resp.status_code == 200:
        print("✅ Note addition successful.")
    else:
        print(f"❌ Note addition failed: {resp.status_code} {resp.text}")

    # 4. Verify Persistence
    print("4. Verifying persistence...")
    resp = requests.get(f"{BASE_URL}/incidents/{incident_id}", headers=headers)
    data = resp.json()
    
    if data["status"] == "investigating":
        print("✅ Status persisted correctly.")
    else:
        print(f"❌ Status mismatch: {data['status']}")

    # Check notes (might not be in get_incident response if we didn't add it to the schema response model)
    # Let's check the response model in incidents.py
    # The get_incident endpoint returns a dict constructed manually. I need to check if I updated it.
    # Wait, I didn't update the get_incident endpoint to return response_notes!
    # I should check that.
    
    # If I didn't update the GET endpoint, the frontend won't see the notes!
    # I need to fix that in the backend code.

if __name__ == "__main__":
    verify()
