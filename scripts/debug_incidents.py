import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

# Force local DB URL
os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/ctdirp"

from src.database import SessionLocal
from src.models.incident import Incident
from sqlalchemy import text

def debug_incidents():
    db = SessionLocal()
    try:
        print("Inserting test incident...")
        from datetime import datetime
        test_inc = Incident(
            title="Debug Test",
            description="Testing enum mapping",
            severity="low",
            status="open",
            timestamp=datetime.utcnow()
        )
        db.add(test_inc)
        db.commit()
        print(f"✅ Inserted incident {test_inc.id}")

        print("Querying incidents...")
        incidents = db.query(Incident).all()
        for i in incidents:
            print(f"ID: {i.id}, Severity: {i.severity} (Type: {type(i.severity)}), Status: {i.status}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_incidents()
