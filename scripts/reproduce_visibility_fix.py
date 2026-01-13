import sys
import os
from sqlalchemy import or_

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

from src.database import SessionLocal
from src.models.user import User
from src.models.server import Server
from src.models.incident import Incident

def reproduce():
    db = SessionLocal()
    try:
        # 1. Setup Data
        print("Setting up test data...")
        
        # Create Analyst
        analyst = db.query(User).filter(User.username == "test_analyst").first()
        if not analyst:
            analyst = User(username="test_analyst", email="test_analyst@example.com", role="analyst")
            db.add(analyst)
            db.commit()
            db.refresh(analyst)
            print(f"Created Analyst: {analyst.id}")
            
        # Create Server
        server = db.query(Server).filter(Server.hostname == "vis-test-server").first()
        if not server:
            server = Server(hostname="vis-test-server", user_id=1) # Owned by Admin
            db.add(server)
            db.commit()
            db.refresh(server)
            print(f"Created Server: {server.id}")
            
        # Assign Server
        if server not in analyst.assigned_servers:
            analyst.assigned_servers.append(server)
            db.commit()
            print("Assigned server to analyst.")
            
        # Create Incident (Simulating Rule Engine)
        inc = Incident(
            title="Visibility Test Incident",
            description="Testing visibility",
            severity="high",
            user_id=1, # Admin owned
            source="vis-test-server" # MATCHING HOSTNAME
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        print(f"Created Incident: {inc.id} with source={inc.source}")
        
        # 2. Test Visibility Logic (from list_incidents)
        print("\n--- Testing Visibility Logic ---")
        
        # Re-fetch analyst to ensure relationships are loaded
        current_user = db.query(User).filter(User.id == analyst.id).first()
        assigned_hostnames = [s.hostname for s in current_user.assigned_servers]
        print(f"Analyst Assigned Hostnames: {assigned_hostnames}")
        
        query = db.query(Incident).filter(
            or_(
                Incident.user_id == current_user.id,
                Incident.source.in_(assigned_hostnames)
            )
        )
        results = query.all()
        
        print(f"Query returned {len(results)} incidents.")
        found = any(i.id == inc.id for i in results)
        
        if found:
            print("✅ SUCCESS: Analyst can see the incident!")
        else:
            print("❌ FAILURE: Incident not found in query results.")
            
        # Cleanup
        db.delete(inc)
        # Keep user/server for reusable testing or delete if preferred
        # db.delete(server)
        # db.delete(analyst)
        db.commit()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
