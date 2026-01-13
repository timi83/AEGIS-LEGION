
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend path - MUST BE BEFORE IMPORTS
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from src.database import DATABASE_URL, Base
from src.models.organization import Organization
from src.models.user import User
from src.models.audit_log import AuditLog
from src.models.incident import Incident
from src.models.rule import Rule
from src.models.server import Server

def migrate_organizations():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Create the new Table
    print("Creating 'organizations' table if not exists...")
    Base.metadata.create_all(bind=engine)

    # 1.5 Ensure 'organization_id' column exists in 'users'
    print("Checking for 'organization_id' column in 'users'...")
    with engine.connect() as conn:
        conn.execute(text("COMMIT")) # Ensure clean transaction
        try:
             conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id)"))
             conn.commit()
             print("Column 'organization_id' verified/added.")
        except Exception as e:
            print(f"Column check warning: {e}")
            conn.rollback()

    # 2. Extract Data
    Session = sessionmaker(bind=engine) # Rebind
    session = Session()
    users = session.query(User).all()
    print(f"Found {len(users)} users.")

    org_map = {} # "Alpha Capital" -> OrganizationObj

    for user in users:
        org_name = user.organization
        if not org_name:
            print(f"Skipping user {user.username} (No Org)")
            continue
        
        # Normalize
        org_name = org_name.strip()

        # Get or Create Org
        if org_name not in org_map:
            # Check DB first
            existing_org = session.query(Organization).filter(Organization.name == org_name).first()
            if existing_org:
                 org_map[org_name] = existing_org
            else:
                print(f"Creating new Organization: '{org_name}'")
                new_org = Organization(name=org_name)
                session.add(new_org)
                session.flush() # Get ID
                org_map[org_name] = new_org
        
        # Link User
        org = org_map[org_name]
        if user.organization_id != org.id:
            print(f"Linking user '{user.username}' to Org '{org.name}' (ID: {org.id})")
            user.organization_id = org.id
            # Also ensure email is unique (already done)
            
    session.commit()
    print("Migration complete!")

if __name__ == "__main__":
    try:
        migrate_organizations()
    except Exception as e:
        print(f"Migration Failed: {e}")
        import traceback
        traceback.print_exc()
