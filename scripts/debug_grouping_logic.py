
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cloud-threat-detection-platform", "backend")))

from src.database import DATABASE_URL, Base
from src.models.incident import Incident
from src.services.rule_engine import _find_existing_incident, _update_existing_incident, _create_incident

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_grouping():
    print(f"Connecting to DB: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    source = "grouping_test_source"
    event_type = "login_failed"
    
    # 1. Clean up previous test data
    print("Cleaning up old debug incidents...")
    db.query(Incident).filter(Incident.description.like(f"%{source}%")).delete(synchronize_session=False)
    db.commit()

    # 2. Create Initial Incident (Simulate Event 1)
    print("Creating initial incident...")
    title = f"Brute-force {event_type} attempt"
    desc = f"Source {source} repeated failures: 5"
    
    # Manually create to ensure we control the state
    inc = Incident(
        title=title,
        description=desc,
        severity="medium",
        status="Open",
        alert_count=1
    )
    db.add(inc)
    db.commit()
    db.refresh(inc)
    print(f"Created Incident ID={inc.id}, Title='{inc.title}', Desc='{inc.description}', AlertCount={inc.alert_count}")

    # 3. Test Find Logic
    print("\nTesting _find_existing_incident...")
    found = _find_existing_incident(db, source, event_type)
    
    if found:
        print(f"✅ Found Incident ID={found.id}")
    else:
        print(f"❌ NOT FOUND. Expected to find ID={inc.id}")
        print(f"Search params: source='{source}', event_type='{event_type}'")
        print(f"DB Incident: Title='{inc.title}', Desc='{inc.description}'")
        return

    # 4. Test Update Logic
    print("\nTesting _update_existing_incident...")
    dummy_event = {"source": source, "event_type": event_type, "count": 2}
    res = _update_existing_incident(db, found, dummy_event)
    
    print(f"Update Result: {res}")
    
    # Verify in DB
    db.refresh(found)
    print(f"DB Alert Count after update: {found.alert_count}")
    
    if found.alert_count == 2:
        print("✅ SUCCESS: Alert count incremented.")
    else:
        print(f"❌ FAILURE: Alert count is {found.alert_count}, expected 2.")

if __name__ == "__main__":
    debug_grouping()
