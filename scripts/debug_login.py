
import requests

url = "http://127.0.0.1:8000/api/token"
payload = {
    "username": "timiabioye11@gmail.com",
    "password": "password123" # Assuming this is the password you used? Or 'password'?
}

# The route expects form data (OAuth2PasswordRequestForm), not JSON
# so we pass data=payload
print(f"Logging in with {payload}...")
try:
    response = requests.post(url, data=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
