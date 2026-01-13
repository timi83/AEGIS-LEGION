import sys
import os

# Add backend directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend')))

from src.database import SessionLocal
from src.models.server import Server
from src.models.user import User

def check_db():
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        server_count = db.query(Server).count()
        
        print(f"Users in DB: {user_count}")
        print(f"Servers in DB: {server_count}")
        
        if server_count > 0:
            servers = db.query(Server).all()
            for s in servers:
                print(f"Server: {s.name} (ID: {s.id}, UserID: {s.user_id}, hostname: {s.hostname})")
        else:
            print("No servers found.")
            
    except Exception as e:
        print(f"Error checking DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
