
import requests
import sys

API_URL = "http://localhost:8000/api"
USER_EMAIL = "agent_runner@test.com"
PASSWORD = "password123"

def get_key():
    # 1. Register (ignore error if exists)
    try:
        requests.post(f"{API_URL}/register", json={
            "username": "agent_runner",
            "email": USER_EMAIL,
            "password": PASSWORD,
            "full_name": "Agent Runner",
            "organization": "AgentCorp"
        })
    except: pass

    # 2. Login
    res = requests.post(f"{API_URL}/token", data={"username": USER_EMAIL, "password": PASSWORD})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        sys.exit(1)
    
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Generate API Key
    # URL should be /api/generate-api-key based on router structure
    res = requests.post(f"{API_URL}/generate-api-key", headers=headers, json={})
    
    if res.status_code == 200:
        print(res.json()["api_key"])
    else:
        # Maybe key already exists? The endpoint might return it?
        # If not, let's assume we can't easily get it back if not returned.
        # But wait, we can't see the key again usually.
        # If generation fails, we might be stuck.
        # Let's hope generation works or returns existing (unlikely for security).
        print(f"Failed to generate key: {res.text}")
        sys.exit(1)

if __name__ == "__main__":
    get_key()
