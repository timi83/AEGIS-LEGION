import requests
import sys
import os

# Add backend directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend')))
from src.database import SessionLocal
from src.models.server import Server # Import Server first to register server_assignments table
from src.models.user import User
from src.models.organization import Organization
from src.models.incident import Incident

def debug_assign():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        print("Admin user not found in DB.")
        return

    # Use email for login if available
    email = admin.email or "admin@example.com"
    print(f"Logging in as {email}...")

    # Login
    try:
        res = requests.post("http://localhost:8001/api/token", data={
            "username": email,
            "password": "password123" # Assuming default password
        })
        if res.status_code != 200:
            print(f"Login failed: {res.text}")
            # Try plain text password if hashed doesn't match default (unlikely for scaffold)
            return
        
        token = res.json()["access_token"]
        print("Login successful. Token acquired.")

        # Call Debug Endpoint
        target = "analyst"
        print(f"Checking assignment for target: {target}")
        
        debug_url = f"http://localhost:8001/api/incidents/debug/assignment-check?target_username={target}"
        res = requests.get(debug_url, headers={"Authorization": f"Bearer {token}"})
        
        print("Debug Response:")
        print(res.json())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_assign()
