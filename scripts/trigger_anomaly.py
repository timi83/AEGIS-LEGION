import requests
import json

def trigger_anomaly():
    url = "http://127.0.0.1:8000/api/ingest/"
    
    # This payload is designed to trigger the anomaly detector's logic
    # (fail_count >= 10 in anomaly_detector.py)
    payload = {
        "source": "test_script",
        "event_type": "login_attempt",
        "details": "Simulated brute force attack",
        "severity": "low", # The detector should upgrade this or create a new high severity incident
        "data": {
            "fail_count": 15, 
            "ip": "192.168.1.100"
        }
    }
    
    try:
        print(f"Sending suspicious event to {url}...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Event sent successfully!")
            print("Response:", response.json())
            print("\nCheck your Dashboard for a 'Anomaly detected' incident!")
        else:
            print(f"❌ Failed to send event: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    trigger_anomaly()
