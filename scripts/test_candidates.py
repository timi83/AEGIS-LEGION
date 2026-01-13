import requests
import sys

def test_candidates():
    # Login as admin
    base_url = "http://localhost:8001/api"
    try:
        # Get Token
        auth = requests.post(f"{base_url}/token", data={"username": "admin@example.com", "password": "password123"})
        token = auth.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get First Incident
        incidents = requests.get(f"{base_url}/incidents/", headers=headers).json()
        if not incidents:
            print("No incidents found.")
            return

        incident_id = incidents[0]["id"]
        print(f"Testing Candidates for Incident #{incident_id} (Source: {incidents[0].get('source')})")
        
        # Get Candidates
        res = requests.get(f"{base_url}/incidents/{incident_id}/candidates", headers=headers)
        if res.status_code == 200:
            candidates = res.json()
            print(f"Found {len(candidates)} candidates:")
            for c in candidates:
                print(f" - {c['username']} ({c['role']})")
        else:
            print(f"Error {res.status_code}: {res.text}")

    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_candidates()
