import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/cloud-threat-detection-platform/backend')

from src.database import SessionLocal
from src.models.rule import Rule

db = SessionLocal()
rules = db.query(Rule).all()
print(f"Found {len(rules)} rules.")
for r in rules:
    print(f"Rule: {r.name}, Enabled: {r.enabled}, Conditions: {r.conditions}")
db.close()
