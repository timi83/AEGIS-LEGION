import requests
import json

def test_ingest():
    url = "http://127.0.0.1:8000/api/ingest/"
    # REPLACE WITH VALID KEY or TOKEN
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "test_key_123" 
    }
    payload = {
        "source": "agent1",
        "event_type": "login_failed",
        "details": "bad password",
        "severity": "high",
        "data": {"fail_count": 12}
    }
    
    try:
        print(f"Sending event to {url}...")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("✅ Event sent successfully!")
            print("Response:", response.json())
        else:
            print(f"❌ Failed to send event: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_ingest()
