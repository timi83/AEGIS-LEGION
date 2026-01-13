import sys
import os
from sqlalchemy import create_engine, text

# Add backend to path to import config if needed, or just hardcode for script
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

# DATABASE_URL = "sqlite:///cloud-threat-detection-platform/backend/ctdirp.db"
DATABASE_URL = "postgresql://postgres:password@localhost:5432/ctdirp"

def migrate():
    print("VERSION 2 - POSTGRES MIGRATION")
    print(f"Migrating database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Check if column exists
            print("Checking for 'source' column in 'incidents' table...")
            # SQLite specific pragmas or just try adding it
            try:
                conn.execute(text("ALTER TABLE incidents ADD COLUMN source VARCHAR(255)"))
                conn.commit()
                print("Successfully added 'source' column.")
            except Exception as e:
                # If it fails, assume it exists or use more robust check
                if "duplicate column" in str(e).lower() or "no such table" not in str(e).lower():
                    print(f"Column might already exist or other error: {e}")
                else:
                    raise e
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
