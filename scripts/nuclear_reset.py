import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

# Force local DB URL
os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/ctdirp"

from src.database import SessionLocal, engine
from src.models.incident import Incident
from sqlalchemy import text

def nuclear_reset():
    db = SessionLocal()
    try:
        print("☢️ INITIATING NUCLEAR RESET ☢️")
        
        # 1. Drop Table
        print("Dropping incidents table...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS incidents CASCADE"))
            conn.commit()
        print("✅ Incidents table dropped.")

        # 2. Drop Enum Types (Postgres specific)
        print("Dropping Enum types...")
        with engine.connect() as conn:
            conn.execute(text("DROP TYPE IF EXISTS severitylevel CASCADE"))
            conn.execute(text("DROP TYPE IF EXISTS incidentstatus CASCADE"))
            conn.commit()
        print("✅ Enum types dropped.")

        # 3. Recreate Tables
        print("Recreating tables...")
        from src.database import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Tables recreated.")
        
        # 4. Insert Test Data
        print("Inserting test incident...")
        from src.models.incident import Incident
        from datetime import datetime
        
        test_inc = Incident(
            event_id="reset-test-id-001",
            title="System Reset",
            description="Database has been reset to use String columns.",
            severity="low",
            status="open",
            timestamp=datetime.utcnow()
        )
        db.add(test_inc)
        db.commit()
        print(f"✅ Inserted test incident: {test_inc.title} (Severity: {test_inc.severity})")

    except Exception as e:
        print(f"❌ Error during reset: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    nuclear_reset()
