import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend')))

from src.database import engine

def migrate_users():
    print("Migrating users table...")
    with engine.connect() as conn:
        try:
            # Check if column exists again just to be safe
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='created_at'"))
            if result.rowcount > 0:
                print("Column 'created_at' already exists.")
                return

            print("Adding 'created_at' column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW()"))
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Error migrating: {e}")

if __name__ == "__main__":
    migrate_users()
