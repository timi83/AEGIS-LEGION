
import requests
import json

url = "http://127.0.0.1:8000/api/register"
payload = {
    "username": "bola",
    "password": "password123",
    "email": "timiabioye11@gmail.com",
    "full_name": "Bola Test",
    "organization": "TestOrg"
}


print(f"Checking GET http://127.0.0.1:8000/health ...")
try:
    h = requests.get("http://127.0.0.1:8000/health", timeout=5)
    print(f"Health: {h.status_code} {h.text}")
except Exception as e:
    print(f"Health check failed: {e}")

print(f"Sending POST to {url} with {payload['email']}...")
try:
    response = requests.post(url, json=payload, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
