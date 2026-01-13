import sys
import os
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cloud-threat-detection-platform", "backend")))

from src.database import DATABASE_URL

def migrate():
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            print("Adding 'alert_count' column to 'incidents' table...")
            conn.execute(text("ALTER TABLE incidents ADD COLUMN alert_count INTEGER DEFAULT 1"))
            conn.commit()
            print("✅ Column added successfully.")
        except Exception as e:
            if "duplicate column" in str(e) or "already exists" in str(e):
                print("ℹ️ Column 'alert_count' already exists.")
            else:
                print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate()
