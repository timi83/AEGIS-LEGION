import requests
import sys

def test_login():
    url = "http://127.0.0.1:8000/api/token"
    payload = {
        "username": "admin",
        "password": "password123"
    }
    
    try:
        print(f"Attempting login to {url}...")
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Login Successful! Token received: {token[:20]}...")
        else:
            print(f"❌ Login Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_login()
