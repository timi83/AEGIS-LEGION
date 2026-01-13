import requests
import sys

API_URL = "http://localhost:8000/api"
USERNAME = "admin@example.com"
PASSWORD = "securepassword"

def check():
    print("Logging in...")
    try:
        resp = requests.post(f"{API_URL}/token", data={"username": USERNAME, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("Fetching Incidents...")
        resp = requests.get(f"{API_URL}/incidents", headers=headers)
        if resp.status_code != 200:
            print(f"Failed to list incidents: {resp.text}")
            return
            
        incidents = resp.json()
        print(f"Found {len(incidents)} incidents.")
        for inc in incidents:
            print(f" - [{inc['id']}] {inc['title']} ({inc['severity']}): {inc['description'][:50]}...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
