import sys
import os
import random
from datetime import datetime, timedelta

# Add backend directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend')))

from src.database import SessionLocal
from src.models.server import Server
from src.models.user import User

def seed_servers():
    db = SessionLocal()
    try:
        # Get the first user (usually admin) to assign servers to
        user = db.query(User).first()
        if not user:
            print("Error: No users found. Please create a user first.")
            return

        print(f"Seeding servers for user: {user.username} (ID: {user.id})")

        servers_data = [
            {
                "name": "Primary-DC-01",
                "hostname": "dc01.internal.corp",
                "ip_address": "10.0.0.5",
                "os_info": "Windows Server 2022",
                "status": "online",
                "last_heartbeat": datetime.utcnow()
            },
            {
                "name": "Web-Prod-01",
                "hostname": "web01.prod.cloud",
                "ip_address": "192.168.1.100",
                "os_info": "Ubuntu 22.04 LTS",
                "status": "online",
                "last_heartbeat": datetime.utcnow() - timedelta(minutes=2)
            },
            {
                "name": "Legacy-DB-03",
                "hostname": "db03.backup.local",
                "ip_address": "10.0.2.15",
                "os_info": "CentOS 7",
                "status": "offline",
                "last_heartbeat": datetime.utcnow() - timedelta(days=2)
            }
        ]

        created_count = 0
        for s_data in servers_data:
            # Check if server already exists to avoid duplicates (by hostname)
            existing = db.query(Server).filter(Server.hostname == s_data["hostname"]).first()
            if not existing:
                new_server = Server(
                    user_id=user.id,
                    name=s_data["name"],
                    hostname=s_data["hostname"],
                    ip_address=s_data["ip_address"],
                    os_info=s_data["os_info"],
                    status=s_data["status"],
                    last_heartbeat=s_data["last_heartbeat"]
                )
                db.add(new_server)
                created_count += 1
                print(f"Adding server: {s_data['name']}")
            else:
                print(f"Server {s_data['name']} already exists, skipping.")

        db.commit()
        print(f"Successfully seeded {created_count} servers.")

    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_servers()
