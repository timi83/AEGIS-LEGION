import requests
import json

def fetch_incidents():
    # Login first to get token
    token_url = "http://127.0.0.1:8000/api/token"
    login_payload = {"username": "admin", "password": "password123"}
    
    try:
        # Get Token
        auth_response = requests.post(token_url, data=login_payload)
        if auth_response.status_code != 200:
            print("❌ Login failed, cannot fetch incidents.")
            return

        token = auth_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Fetch Incidents
        incidents_url = "http://127.0.0.1:8000/api/incidents/"
        print(f"Fetching incidents from {incidents_url}...")
        response = requests.get(incidents_url, headers=headers)
        
        if response.status_code == 200:
            incidents = response.json()
            print(f"✅ Successfully fetched {len(incidents)} incidents:")
            for inc in incidents:
                print(f" - ID: {inc['id']} | Title: {inc['title']} | Severity: {inc['severity']} | Status: {inc['status']}")
        else:
            print(f"❌ Failed to fetch incidents: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    fetch_incidents()
