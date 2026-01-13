import requests
import time
import uuid

def verify_deduplication():
    base_url = "http://127.0.0.1:8000/api"
    # Generate a fixed ID for this test run
    fixed_event_id = str(uuid.uuid4())
    
    print(f"🧪 Starting Deduplication Test (Event ID: {fixed_event_id})")
    print("-" * 50)

    payload = {
        "event_id": fixed_event_id,
        "source": "dedup_tester",
        "event_type": "duplicate_attack",
        "details": "This event is sent twice to test deduplication.",
        "severity": "medium",
        "data": {"attempt": 1}
    }

    # 1. Send First Event
    print("1. Sending FIRST event...")
    try:
        resp1 = requests.post(f"{base_url}/ingest/", json=payload)
        if resp1.status_code == 200:
            print("   ✔ First event sent successfully.")
        else:
            print(f"   ❌ First event failed: {resp1.status_code} {resp1.text}")
            return
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return

    # Wait for consumer to process
    time.sleep(2)

    # 2. Send Second Event (Duplicate)
    print("\n2. Sending SECOND event (Duplicate)...")
    try:
        resp2 = requests.post(f"{base_url}/ingest/", json=payload)
        if resp2.status_code == 200:
            print("   ✔ Second event sent successfully (API should accept it).")
        else:
            print(f"   ❌ Second event failed: {resp2.status_code}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")

    # Wait for consumer to process
    time.sleep(2)

    # 3. Verify Incidents in DB
    print("\n3. Verifying Incidents in Database...")
    
    # Login to get token
    try:
        auth_resp = requests.post(f"{base_url}/token", data={"username": "admin", "password": "password123"})
        if auth_resp.status_code != 200:
            # Try creating admin if missing (since we just reset DB)
            print("   ⚠ Login failed. Attempting to create admin user...")
            # This part assumes check_user.py logic or similar, but for now let's just fail if login fails
            # Actually, nuclear_reset.py might not have created the admin user? 
            # Let's check if we need to run check_user.py first.
            print("   ❌ Login failed. Please run 'py scripts/check_user.py' to restore admin user.")
            return
            
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"   ❌ Login connection failed: {e}")
        return

    # Fetch Incidents
    try:
        inc_resp = requests.get(f"{base_url}/incidents/", headers=headers)
        if inc_resp.status_code == 200:
            incidents = inc_resp.json()
            
            # Count matches
            matches = [i for i in incidents if i.get("description") and fixed_event_id in str(i)]
            # Alternatively, if we exposed event_id in the API response, we could check that.
            # But currently IncidentResponse schema might not have event_id. 
            # Let's rely on description or title if event_id isn't in response.
            # Wait, I didn't update the Pydantic schema to include event_id in response.
            # So I can't check event_id directly from API unless I update schema.
            # However, the consumer puts details in description: "Event: {...}" which might contain it?
            # Or simpler: The consumer logs "Skipping duplicate".
            
            # Let's check how many incidents have the specific details
            count = 0
            for inc in incidents:
                # The description set by consumer: f"Matched rule {rule.name}. Event: {event.get('details')}"
                # Our details: "This event is sent twice to test deduplication."
                if "This event is sent twice to test deduplication." in inc.get("description", ""):
                    count += 1
            
            print(f"   📊 Found {count} incident(s) for this event.")
            
            if count == 1:
                print("   ✅ SUCCESS: Deduplication worked! Only 1 incident created.")
            elif count == 0:
                print("   ❌ FAILURE: No incidents found. Consumer might be broken.")
            else:
                print(f"   ❌ FAILURE: Found {count} incidents. Deduplication failed.")
                
        else:
            print(f"   ❌ Fetch incidents FAILED: {inc_resp.status_code}")
    except Exception as e:
        print(f"   ❌ Fetch connection failed: {e}")

if __name__ == "__main__":
    verify_deduplication()
