import sys
import os
import requests
import random
import string

# Setup imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from src.database import SessionLocal, init_db
from src.models.user import User
from src.models.server import Server
from src.auth.security import create_access_token
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def verify_server_permissions():
    db = SessionLocal()
    try:
        # 1. Create Users
        org = f"TestOrg_{get_random_string()}"
        
        # Admin
        admin_prob = f"admin_{get_random_string()}"
        admin = User(
            username=admin_prob,
            email=f"{admin_prob}@test.com",
            hashed_password=pwd_context.hash("password"),
            role="admin",
            organization=org
        )
        db.add(admin)
        
        # Viewer
        viewer_prob = f"viewer_{get_random_string()}"
        viewer = User(
            username=viewer_prob,
            email=f"{viewer_prob}@test.com",
            hashed_password=pwd_context.hash("password"),
            role="viewer",
            organization=org
        )
        db.add(viewer)
        db.commit()
        db.refresh(admin)
        db.refresh(viewer)
        
        # 2. Create Server owned by Viewer
        server_name = f"server_{get_random_string()}"
        server = Server(
            name=server_name,
            hostname=f"host_{get_random_string()}",
            ip_address="192.168.1.100",
            os_info="Linux",
            status="online",
            user_id=viewer.id
        )
        db.add(server)
        db.commit()
        db.refresh(server)
        
        print(f"Created Admin ({admin.id}), Viewer ({viewer.id}), and Server ({server.id}) owned by Viewer.")
        
        # 3. Mint Token for Admin
        access_token = create_access_token(data={"sub": admin.username})
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 4. Attempt Rename via API
        new_name = f"Renamed_By_Admin_{get_random_string()}"
        url = f"http://127.0.0.1:8000/api/servers/{server.id}"
        print(f"Attempting to rename server {server.id} to '{new_name}' as Admin...")
        
        response = requests.put(url, json={"name": new_name}, headers=headers)
        
        if response.status_code == 200:
            print("✅ Success! Admin renamed the server.")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_server_permissions()
