
import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend', '.env'))

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, DATABASE_URL
from src.models.incident import Incident
from src.models.user import User
from src.models.organization import Organization
from src.models.server import Server
from src.models.rule import Rule
from src.models.audit_log import AuditLog
from src.models.incident_note import IncidentNote
from src.models.notification import Notification

# Connect
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def migrate():
    print("🚀 Starting Scoped ID Migration...")
    
    # 0. Alter Table (DDL) - Hacky but effective for prototyping
    # Check if columns exist or just try to add them and ignore error
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS org_incident_id INTEGER;"))
            conn.execute(text("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS organization_id INTEGER;"))
            conn.commit()
            print("✅ Columns added (or already existed).")
    except Exception as e:
        print(f"⚠️ DDL Error (might be fine): {e}")

    # 1. Fetch all incidents
    incidents = db.query(Incident).order_by(Incident.timestamp.asc()).all()
    print(f"found {len(incidents)} total incidents.")
    
    # 2. Group by Org and assign IDs
    org_counters = {} # { org_id: current_count }
    
    updates = 0
    for inc in incidents:
        # Resolve Org ID if missing
        if not inc.organization_id:
            if inc.user_id:
                user = db.query(User).filter(User.id == inc.user_id).first()
                if user and user.organization_id:
                    inc.organization_id = user.organization_id
            
            # Fallback for orphaned
            if not inc.organization_id:
                print(f"⚠️ Incident {inc.id} has no Org ID. Skipping scope.")
                continue
                
        # Update Counter
        current_count = org_counters.get(inc.organization_id, 0)
        new_count = current_count + 1
        org_counters[inc.organization_id] = new_count
        
        # Assign
        if not inc.org_incident_id:
            inc.org_incident_id = new_count
            updates += 1
            print(f"   -> Incident {inc.id} assigned ID #{new_count} (Org {inc.organization_id})")

    db.commit()
    print(f"✅ Migration Complete. Updated {updates} incidents.")

if __name__ == "__main__":
    migrate()
