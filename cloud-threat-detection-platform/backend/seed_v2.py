import sys
import os
from datetime import datetime, timedelta

# Add backend directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend')))

from src.database import SessionLocal
from src.models.server import Server
from src.models.user import User

def seed_servers_all():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found.")
            return

        print(f"Found {len(users)} users. Checking servers for each...")

        base_servers = [
            {
                "name": "Primary-DC-01",
                "hostname": "dc01.internal.corp",
                "ip_address": "10.0.0.5",
                "os_info": "Windows Server 2022",
                "status": "online"
            },
            {
                "name": "Web-Prod-01",
                "hostname": "web01.prod.cloud",
                "ip_address": "192.168.1.100",
                "os_info": "Ubuntu 22.04 LTS",
                "status": "online"
            },
            {
                "name": "Legacy-DB-03",
                "hostname": "db03.backup.local",
                "ip_address": "10.0.2.15",
                "os_info": "CentOS 7",
                "status": "offline"
            }
        ]

        total_added = 0
        for user in users:
            print(f"Checking User: {user.username} (ID: {user.id})...")
            
            # Check if this user already has servers
            count = db.query(Server).filter(Server.user_id == user.id).count()
            if count > 0:
                print(f"  - Already has {count} servers. Skipping.")
                continue

            # Add servers for this user
            for s_data in base_servers:
                new_server = Server(
                    user_id=user.id,
                    name=s_data["name"],
                    hostname=f"{s_data['hostname']}-{user.id}", # Make hostname unique per user just in case
                    ip_address=s_data["ip_address"],
                    os_info=s_data["os_info"],
                    status=s_data["status"],
                    last_heartbeat=datetime.utcnow()
                )
                db.add(new_server)
                total_added += 1
            print(f"  - Added 3 servers.")

        db.commit()
        print(f"Successfully added {total_added} servers across all users.")

    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_servers_all()
