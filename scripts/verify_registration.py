
import requests
import secrets

BASE_URL = "http://localhost:8000/api"

def test_register():
    # Generate unique user
    username = f"testuser_{secrets.token_hex(4)}"
    email = f"{username}@example.com"
    password = "a_very_long_password_that_might_trigger_limitations_if_not_handled_correctly_by_the_backend_hashing_function_which_has_a_72_byte_limit"
    
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Test User",
        "organization": "Test Org",
        "role": "admin"
    }

    print(f"DEBUG: Attempting to register {username}...")
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"DEBUG: Status Code: {r.status_code}")
        print(f"DEBUG: Response: {r.text}")
        
        if r.status_code == 200:
            print("SUCCESS: Registration successful!")
        else:
            print("FAILURE: Registration failed.")
    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    test_register()
