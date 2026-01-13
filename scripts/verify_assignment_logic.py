import sys
import os
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models.user import User
from src.models.incident import Incident
from src.models.notification import Notification
from src.models.incident import incident_assignments

# DB Connection
DATABASE_URL = "postgresql://postgres:password@db:5432/ctdirp" 
# NOTE: Using localhost because running from host machine scripts. 
# Make sure port 5432 is exposed.

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def verify():
    print("🧪 Verifying Assignment Logic...")
    
    # 1. Get a test user
    user = db.query(User).first()
    if not user:
        print("❌ No users found. Cannot test.")
        return

    # 2. Get/Create an incident
    incident = db.query(Incident).first()
    if not incident:
        print("❌ No incidents found. Cannot test.")
        return

    print(f"👤 User: {user.username} (ID: {user.id})")
    print(f"🔥 Incident: {incident.title} (ID: {incident.id})")

    # 3. Simulate Assignment Logic manually (API Logic)
    # Check if already assigned
    if user not in incident.assignees:
        print("   -> Assigning User to Incident...")
        incident.assignees.append(user)
        
        # Create Notification
        notif = Notification(
            user_id=user.id,
            title=f"TEST ASSIGNMENT #{incident.id}",
            message="Test notification",
            link="/dashboard"
        )
        db.add(notif)
        db.commit()
    else:
        print("   -> User already assigned. Skipping add.")

    # 4. Refresh and Verify
    db.expire_all()
    
    # Check Relationship
    incident = db.query(Incident).filter(Incident.id == incident.id).first()
    assignees = incident.assignees
    print(f"✅ Incident Assignees: {[u.username for u in assignees]}")

    if user in assignees:
        print("   PASS: User is in assignees list.")
    else:
        print("❌ FAIL: User NOT in assignees list after commit.")

    # Check Notification
    notif = db.query(Notification).filter(Notification.title == f"TEST ASSIGNMENT #{incident.id}").first()
    if notif:
        print(f"✅ Notification Found: {notif.title} for User {notif.user_id}")
    else:
        print("❌ FAIL: Notification not found.")

if __name__ == "__main__":
    verify()
