import requests

def test_login():
    url = "http://127.0.0.1:8000/api/token"
    payload = {
        "username": "admin",
        "password": "password123"
    }
    print(f"Attempting login to {url} with {payload['username']}...")
    
    try:
        resp = requests.post(url, data=payload)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ Login Successful!")
            print("Token:", resp.json().get("access_token")[:20] + "...")
        else:
            print("❌ Login Failed")
            print("Response:", resp.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
