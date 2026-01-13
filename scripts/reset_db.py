
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cloud-threat-detection-platform", "backend")))

from src.database import engine, Base
from src.models.user import User
from src.models.incident import Incident
from src.models.rule import Rule
from src.models.server import Server

def reset_database():
    print("⚠️  DANGER: This will DROP all tables and delete all data!")
    confirm = input("Are you sure? (type 'yes' to confirm): ")
    if confirm != "yes":
        print("Aborted.")
        return

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")

    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    print("✅ Database reset complete. You can now restart the backend.")

if __name__ == "__main__":
    reset_database()
