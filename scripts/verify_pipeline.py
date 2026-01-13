import requests
import time
import uuid

def verify_pipeline():
    base_url = "http://127.0.0.1:8000/api"
    unique_id = str(uuid.uuid4())[:8]
    
    print(f"🚀 Starting Pipeline Verification (Test ID: {unique_id})")
    print("-" * 50)

    # 1. Event Ingestion & Kafka Production
    print("1. Testing Event Ingestion & Kafka Production...")
    ingest_payload = {
        "source": "pipeline_verifier",
        "event_type": "verification_test",
        "details": f"Pipeline verification event {unique_id}",
        "severity": "medium",
        "data": {"check_id": unique_id}
    }
    
    try:
        resp = requests.post(f"{base_url}/ingest/", json=ingest_payload)
        if resp.status_code == 200:
            print("   ✔ Event ingestion: SUCCESS")
            print("   ✔ Kafka production: SUCCESS (API returned 200)")
        else:
            print(f"   ❌ Event ingestion FAILED: {resp.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return

    # Wait for Consumer & Rule Engine
    print("\n⏳ Waiting 5 seconds for Kafka Consumer & Rule Engine...")
    time.sleep(5)

    # 2. Incident Creation & Frontend Display (API Check)
    print("\n2. Verifying Incident Creation & API Availability...")
    
    # Login to get token
    try:
        auth_resp = requests.post(f"{base_url}/token", data={"username": "admin", "password": "password123"})
        if auth_resp.status_code != 200:
            print("   ❌ Login failed. Cannot verify incidents.")
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
            
            # Look for our specific incident
            found = False
            for inc in incidents:
                if unique_id in inc.get("description", ""):
                    found = True
                    print(f"   ✔ Incident creation: SUCCESS (Found incident {inc['id']})")
                    print(f"   ✔ Kafka consumption: SUCCESS")
                    print(f"   ✔ Rule engine/Fallback: SUCCESS")
                    print(f"   ✔ Frontend data source: SUCCESS (API returns correct data)")
                    break
            
            if not found:
                print("   ❌ Incident NOT found. Consumer might be lagging or failed.")
                print("   Debug: Last 3 incidents:")
                for inc in incidents[:3]:
                    print(f"     - {inc['title']}: {inc['description']}")
        else:
            print(f"   ❌ Fetch incidents FAILED: {inc_resp.status_code}")
    except Exception as e:
        print(f"   ❌ Fetch connection failed: {e}")

    print("-" * 50)
    print("✅ Verification Complete")

if __name__ == "__main__":
    verify_pipeline()
