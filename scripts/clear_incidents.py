import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

# Force local DB URL for script execution
os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/ctdirp"

from src.database import SessionLocal
from src.models.incident import Incident
from sqlalchemy import text

def clear_incidents():
    db = SessionLocal()
    try:
        print("Deleting all incidents...")
        db.query(Incident).delete()
        db.commit()
        print("✅ Incidents table cleared.")
    except Exception as e:
        print(f"❌ Error clearing incidents: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_incidents()
