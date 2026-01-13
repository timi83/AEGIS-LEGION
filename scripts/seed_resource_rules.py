
import sys
import os
import json
from datetime import datetime

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from src.database import SessionLocal, engine
from src.models.rule import Rule
from src.models.user import User
from src.models.organization import Organization
from src.models.audit_log import AuditLog
from src.models.incident import Incident

def seed_resource_rules():
    db = SessionLocal()
    try:
        print("Checking for existing High Resource rules...")
        existing = db.query(Rule).filter(Rule.name == "High CPU Usage").first()
        
        if existing:
            print("Rule 'High CPU Usage' already exists.")
            return

        print("Creating 'High CPU Usage' rule...")
        # Rule: CPU > 90%
        cpu_rule = Rule(
            name="High CPU Usage",
            description="Detects if CPU usage exceeds 90%",
            conditions=json.dumps([{"field": "cpu", "op": "gt", "value": "90"}]),
            severity="high",
            enabled=True,
            created_at=datetime.utcnow()
        )
        
        db.add(cpu_rule)
        db.commit()
        print("✅ Rule 'High CPU Usage' created successfully.")
        
    except Exception as e:
        print(f"❌ Error seeding rules: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_resource_rules()
