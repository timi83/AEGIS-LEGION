import sys
import os

# Add backend directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend')))

from src.database import engine, Base
from src.models.audit_log import AuditLog
from src.models.user import User

def create_tables():
    print("Creating tables...")
    try:
        # Create all tables defined in Base metadata
        # This will skip existing tables and only create missing ones (like audit_logs)
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
