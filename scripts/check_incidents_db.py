import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

from src.database import SessionLocal
from src.models.incident import Incident

def check():
    db = SessionLocal()
    try:
        incidents = db.query(Incident).all()
        print(f"Found {len(incidents)} total incidents in DB.")
        for inc in incidents:
            print(f" - [{inc.id}] Title: {inc.title} | User: {inc.user_id} | Source: {inc.source} | Sev: {inc.severity}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
