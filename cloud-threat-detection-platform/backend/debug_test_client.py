from fastapi.testclient import TestClient
from main import app
import sys

# Force plaintext verification logic if not already loaded?
# app startup event runs automatically with TestClient? No, TestClient uses Starlette LifeSpan.
# But startup event logic (DB init) is fine.

try:
    print("Initializing TestClient...")
    with TestClient(app) as client:
        print("Sending POST /api/token request in-process...")
        response = client.post("/api/token", data={"username": "timia", "password": "password123"})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login Successful (In-Process)")
        else:
            print("❌ Login Failed (In-Process)")
except Exception as e:
    print(f"❌ CRASH In-Process: {e}")
    import traceback
    traceback.print_exc()
