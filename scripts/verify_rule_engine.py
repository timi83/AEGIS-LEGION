
import sys
import os
import requests
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

API_URL = "http://127.0.0.1:8000/api"

def test_fallback_rule():
    print("\n--- Testing Fallback Rule (Login Failure) ---")
    payload = {
        "source": "test_script",
        "event_type": "login_failed",
        "details": "Simulated brute force",
        "severity": "medium",
        "data": {"fail_count": 5}
    }
    
    try:
        # Send event
        print(f"Sending event: {payload}")
        res = requests.post(f"{API_URL}/ingest/", json=payload)
        if res.status_code == 200:
            print("Event ingested successfully.")
        else:
            print(f"Ingest failed: {res.status_code} {res.text}")
            return

        # Wait for processing
        time.sleep(2)

        # Check for incident
        print("Checking for created incident...")
        res = requests.get(f"{API_URL}/incidents/")
        if res.status_code == 200:
            incidents = res.json()
            # Look for the incident
            found = False
            for inc in incidents:
                if inc["title"] == "Brute-force: multiple login failures" and "test_script" in inc["description"]:
                    print(f"✅ SUCCESS: Found incident #{inc['id']}: {inc['title']}")
                    found = True
                    break
            if not found:
                print("❌ FAILURE: Incident not found.")
        else:
            print(f"Failed to fetch incidents: {res.status_code}")

    except Exception as e:
        print(f"Error: {e}")

def test_critical_fallback():
    print("\n--- Testing Fallback Rule (Malware Detected) ---")
    payload = {
        "source": "test_host",
        "event_type": "malware_detected",
        "details": "Trojan.Win32.Generic",
        "severity": "high"
    }
    
    try:
        # Send event
        print(f"Sending event: {payload}")
        res = requests.post(f"{API_URL}/ingest/", json=payload)
        if res.status_code == 200:
            print("Event ingested successfully.")
        else:
            print(f"Ingest failed: {res.status_code} {res.text}")
            return

        # Wait for processing
        time.sleep(2)

        # Check for incident
        print("Checking for created incident...")
        res = requests.get(f"{API_URL}/incidents/")
        if res.status_code == 200:
            incidents = res.json()
            # Look for the incident
            found = False
            for inc in incidents:
                if "Critical security alert" in inc["title"] and "malware_detected" in inc["title"]:
                    print(f"✅ SUCCESS: Found incident #{inc['id']}: {inc['title']}")
                    found = True
                    break
            if not found:
                print("❌ FAILURE: Incident not found.")
        else:
            print(f"Failed to fetch incidents: {res.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fallback_rule()
    test_critical_fallback()
