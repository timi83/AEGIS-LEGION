import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def debug_api():
    # 1. Login
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "password123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")
    except Exception as e:
        print(f"Login error: {e}")
        return

    # 2. Get Rules
    print("\nFetching rules...")
    try:
        resp = requests.get(f"{BASE_URL}/rules/", headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Fetch error: {e}")

    # 3. Create Rule
    print("\nCreating rule...")
    payload = {
        "name": "Debug Rule API",
        "description": "Test rule",
        "severity": "low",
        "conditions": [{"field": "test", "op": "equals", "value": "1"}],
        "enabled": True
    }
    try:
        resp = requests.post(f"{BASE_URL}/rules/", json=payload, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Create error: {e}")

if __name__ == "__main__":
    debug_api()
