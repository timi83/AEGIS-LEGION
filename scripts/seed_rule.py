import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/cloud-threat-detection-platform/backend')

from src.database import SessionLocal
from src.models.rule import Rule
from datetime import datetime
import json

db = SessionLocal()

# Cleanup old test rules matching this name
db.query(Rule).filter(Rule.name == "Debug CPU Rule").delete()
db.commit()

# Create Strict Rule
rule = Rule(
    name="Debug CPU Rule",
    description="Debugging rule engine",
    conditions=json.dumps([{"field": "cpu", "op": "gt", "value": "0.01"}]),
    severity="high",
    enabled=True,
    created_at=datetime.utcnow()
)

db.add(rule)
db.commit()
print(f"Created Rule ID: {rule.id}")
db.close()
