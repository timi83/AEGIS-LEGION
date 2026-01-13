from src.database import SessionLocal, engine, Base
from src.models.rule import Rule
from datetime import datetime
import json

# Ensure tables exist
print(f"Connecting to: {engine.url}")
try:
    Rule.__table__.create(bind=engine, checkfirst=True)
    print("Rules table created (or already exists).")
except Exception as e:
    print(f"Error creating rules table: {e}")

db = SessionLocal()

# Check if rules exist
try:
    count = db.query(Rule).count()
    if count == 0:
        print("Seeding default rules...")
        default_rules = [
            Rule(
                name="High Failure Rate",
                description="Detects if login failures exceed 5 in 1 minute",
                conditions=json.dumps([{"field": "data.fail_count", "op": "gt", "value": "5"}]),
                severity="high",
                enabled=True,
                created_at=datetime.utcnow()
            ),
            Rule(
                name="Root Login Attempt",
                description="Detects any login attempt with username 'root'",
                conditions=json.dumps([{"field": "data.username", "op": "equals", "value": "root"}]),
                severity="critical",
                enabled=True,
                created_at=datetime.utcnow()
            )
        ]
        db.add_all(default_rules)
        db.commit()
        print("Rules seeded successfully.")
    else:
        print("Rules already exist.")
except Exception as e:
    print(f"Error seeding rules: {e}")

db.close()
