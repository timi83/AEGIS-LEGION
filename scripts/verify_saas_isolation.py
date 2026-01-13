import requests
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent dir to path to import models if needed, but we used direct requests mostly
sys.path.append(os.path.join(os.getcwd(), 'cloud-threat-detection-platform', 'backend'))

# Database Setup (Direct insert for bootstrap)
DATABASE_URL = "postgresql://postgres:password@localhost:5432/ctdirp"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

BASE_URL = "http://127.0.0.1:8000/api"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def bootstrap_org_admin(username, password, org):
    """Directly insert an admin for an Org so we can test API from there."""
    db = SessionLocal()
    try:
        # CLEANUP: Delete user if exists to ensure clean state
        db.execute(text("DELETE FROM users WHERE username = :u"), {"u": username})
        db.commit()

        # DYNAMICALLY FETCH WORKING HASH from 'string' user
        # This avoids copy-paste errors
        string_user = db.execute(text("SELECT hashed_password FROM users WHERE username = 'string'")).fetchone()
        if not string_user:
            print("Error: 'string' user not found. Cannot bootstrap.")
            return
        
        pw_hash = string_user[0]
        
        db.execute(text("""
            INSERT INTO users (username, email, hashed_password, role, organization, is_active, created_at)
            VALUES (:u, :e, :p, 'admin', :o, true, now())
        """), {"u": username, "e": f"{username}@test.com", "p": pw_hash, "o": org})
        db.commit()
        print(f"Bootstrapped {username} for {org}")
        
    except Exception as e:
        print(f"Error bootstrapping: {e}")
    finally:
        db.close()

def get_token(username, password):
    resp = requests.post(f"{BASE_URL}/token", data={"username": username, "password": password})
    if resp.status_code != 200:
        print(f"Login failed for {username}: {resp.status_code} {resp.text}")
        return None
    return resp.json()["access_token"]

def verify_isolation():
    print("--- 1. Bootstrapping Tenant Admins (DB Insert) ---")
    bootstrap_org_admin("admin_red", "string", "RedCorp") 
    
    print("\n--- 2. Login as 'string' user (Org: None) ---")
    # We use the known working user 'string'
    token_string = get_token("string", "string")
    
    if not token_string:
        print("Failed to get token for 'string'. Aborting.")
        return

    print("Token acquired for 'string'.")

    print("\n--- 3. Verifying Isolation ---")
    # 'string' user (Org=None) should NOT see 'admin_red' (Org='RedCorp')
    headers = {"Authorization": f"Bearer {token_string}"}
    resp = requests.get(f"{BASE_URL}/users", headers=headers)
    
    if resp.status_code != 200:
        print(f"Failed to list users: {resp.status_code} {resp.text}")
        return

    users = resp.json()
    print(f"'string' user sees {len(users)} users:")
    
    found_red = False
    for u in users:
        print(f" - {u['username']} (Org: {u.get('organization')})")
        if u['username'] == 'admin_red':
            found_red = True
            
    if not found_red:
        print("\nSUCCESS: 'string' user CANNOT see 'admin_red'. Isolation is WORKING.")
    else:
        print("\nFAILURE: 'string' user SAW 'admin_red'. Isolation BROKEN.")

if __name__ == "__main__":
    verify_isolation()
