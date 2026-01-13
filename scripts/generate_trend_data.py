import requests
import time
import random
import uuid

def generate_trend():
    base_url = "http://127.0.0.1:8000/api"
    print("🚀 Generating Trend Data...")
    print("Sending 10 events over 10 seconds to populate the graph...")

    for i in range(1, 11):
        event_id = str(uuid.uuid4())
        payload = {
            "event_id": event_id,
            "source": "trend_generator",
            "event_type": "login_attempt",
            "details": f"Trend test event {i}",
            "severity": random.choice(["low", "medium", "high"]),
            "data": {"attempt": i}
        }
        
        try:
            resp = requests.post(f"{base_url}/ingest/", json=payload)
            if resp.status_code == 200:
                print(f"   [{i}/10] Event sent! (Severity: {payload['severity']})")
            else:
                print(f"   [{i}/10] Failed: {resp.status_code}")
        except Exception as e:
            print(f"   [{i}/10] Error: {e}")
            
        # Sleep for a random short interval to simulate traffic
        time.sleep(random.uniform(0.5, 1.5))

    print("\n✅ Batch complete! Check the Threat Trend graph.")

if __name__ == "__main__":
    generate_trend()
