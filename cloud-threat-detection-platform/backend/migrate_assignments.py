import os
import sys

# Ensure python path includes backend
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, ForeignKey, inspect
from src.database import Base

# Connection (Docker Network)
DATABASE_URL = "postgresql://postgres:password@db:5432/ctdirp"
engine = create_engine(DATABASE_URL)

def migrate():
    print("🚀 Starting Migration: incident_assignments table...")
    
    # Import models so Base.metadata has them
    from src.models.incident import Incident
    from src.models.user import User

    # Use the shared Base.metadata which has 'incidents' and 'users'
    assignments_table = Table(
        'incident_assignments', Base.metadata,
        Column('incident_id', Integer, ForeignKey('incidents.id'), primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
        extend_existing=True
    )

    inspector = inspect(engine)
    if 'incident_assignments' in inspector.get_table_names():
        print("✅ Table 'incident_assignments' already exists. Skipping.")
    else:
        print("⚙️ Creating table 'incident_assignments'...")
        Base.metadata.create_all(engine)
        print("✅ Table created successfully.")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
