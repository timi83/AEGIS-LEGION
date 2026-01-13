
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "postgresql://postgres:password@localhost:5432/ctdirp"

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Checking rules table schema...")
        
        # Check if column exists
        try:
            conn.execute(text("SELECT organization_id FROM rules LIMIT 1"))
            print("✅ Column 'organization_id' already exists.")
        except Exception:
            print("⚠️ Column 'organization_id' missing. Adding it...")
            conn.execute(text("ALTER TABLE rules ADD COLUMN organization_id INTEGER"))
            print("✅ Added 'organization_id'.")
        
        try:
            conn.execute(text("SELECT organization FROM rules LIMIT 1"))
            print("✅ Column 'organization' already exists.")
        except Exception:
            print("⚠️ Column 'organization' missing. Adding it...")
            conn.execute(text("ALTER TABLE rules ADD COLUMN organization VARCHAR(255)"))
            print("✅ Added 'organization'.")

        # Backfill?
        # Ideally, we should set a default organization for existing rules or leave them global (NULL).
        # Let's verify existing rules count only.
        result = conn.execute(text("SELECT COUNT(*) FROM rules"))
        count = result.scalar()
        print(f"INFO: There are {count} existing rules. They will have NULL organization (Global).")
        
        conn.commit()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
