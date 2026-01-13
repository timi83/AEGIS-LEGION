# scripts/migrate_db_step7.py
import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend'))

from src.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        print("Checking for 'response_notes' column in 'incidents' table...")
        # Check if column exists
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='incidents' AND column_name='response_notes'"))
        if result.fetchone():
            print("✅ Column 'response_notes' already exists.")
        else:
            print("⚠️ Column 'response_notes' missing. Adding it now...")
            db.execute(text("ALTER TABLE incidents ADD COLUMN response_notes TEXT DEFAULT ''"))
            db.commit()
            print("✅ Column 'response_notes' added successfully.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
