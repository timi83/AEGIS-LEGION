
import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def run_test():
    import time
    timestamp = int(time.time())
    admin_data = {
        "username": f"email_admin_{timestamp}",
        "password": "SecurePass123!",
        "email": f"real_admin_{timestamp}@company.com", # Dynamic email dest
        "full_name": "Email Admin",
        "organization": "EmailCorp",
        "role": "admin"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        if resp.status_code == 200:
            print("✅ Admin Registered")
        else:
            print(f"❌ Admin Registration Failed: {resp.text}")
            return # Blocked
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # Login
    token_resp = requests.post(f"{BASE_URL}/auth/token", data={"username": admin_data["username"], "password": admin_data["password"]})
    token = token_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"🔑 Token obtained")

    print("\n--- 2. Creating Sub-User ---")
    sub_user_data = {
        "username": "email_user_01",
        "password": "UserPass123!",
        "email": "new_hire@company.com",
        "full_name": "New Hire",
        "role": "viewer"
    }
    resp = requests.post(f"{BASE_URL}/auth/users", json=sub_user_data, headers=headers)
    if resp.status_code == 200:
        print("✅ Sub-User Created (Should trigger 2 emails)")
    else:
        print(f"❌ Sub-User Creation Failed: {resp.text}")

    print("\n--- 3. Generating API Key ---")
    resp = requests.post(f"{BASE_URL}/auth/generate-api-key", headers=headers)
    if resp.status_code == 200:
        print("✅ API Key Generated")
    else:
        print(f"❌ API Key Generation Failed: {resp.text}")

    print("\n--- 4. Triggering Critical Incident (via Kafka) ---")
    # We need to install kafka-python or just use the ingest endpoint if available.
    # checking if ingest endpoint exists... assuming /api/ingest/events or similar?
    # Actually, we can just use the 'test_ingest.py' logic or assume manual Kafka push.
    # Let's try to simulate via a utility script or just trust the auth parts first.
    # WAIT! kafka_producer.py might exist in backend/src/services?
    # Or just use the existing `scripts/test_ingest_curl.py` approach if it calls an API.
    # If no API, I'll use the python script to produce to Kafka if library installed.
    # Assuming 'kafka-python' is not in this script's environment.
    # I will rely on `kafka-console-producer` if available or just skip this part for HEAD.
    # Actually I can use requests to hit the /ingest endpoint if I created one?
    # Looking at open files... `scripts/test_ingest_curl.py` suggests `http://localhost:8000/api/ingest`.
    
    event_payload = {
        "event_id": "evt_crit_email_01",
        "event_type": "security_alert",
        "severity": "critical",
        "source": "firewall",
        "details": "Massive DDoS Detection",
        "user_id": resp.json().get("id", 1), # Wait, api key resp doesn't give ID. 
        # I need the user ID of the sub-user or admin. 
        # Let's use the Admin's ID derived from "me" endpoint
    }
    
    me_resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    user_id = me_resp.json()["id"]
    event_payload["user_id"] = user_id
    
    print(f"Sending Critical Event for User ID {user_id}...")

    try:
        # Use simple requests to ingest endpoint found in test_ingest_curl.py
        # /api/ingest/ (trailing slash might matter)
        ingest_url = f"{BASE_URL}/ingest/" 
        resp = requests.post(ingest_url, json=event_payload, headers=headers)
        
        print(f"Ingest Response: {resp.status_code}")
        if resp.status_code == 200:
             print("✅ Critical Event Ingested (Should trigger alert)")
        else:
             print(f"❌ Ingest Failed: {resp.text}")

    except Exception as e:
        print(f"⚠️ Could not POST event via API: {e}")

if __name__ == "__main__":
    run_test()
