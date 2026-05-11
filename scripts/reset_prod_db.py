
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def reset_db():
    print("!!! DANGER ZONE !!!")
    print("This script will DELETE ALL USERS and ORGANIZATIONS from the database.")
    print("You will lose all accounts!")
    print("----------------------------------------------------------------")
    
    db_url = input("Enter the EXTERNAL Database URL (from Render Dashboard): ").strip()
    
    if not db_url.startswith("postgres"):
        print("❌ Invalid URL. Must start with postgres:// or postgresql://")
        return

    # Fix Render's "postgres://" (deprecated) to "postgresql://" for SQLAlchemy
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    confirm = input("Type 'DELETE EVERYTHING' to confirm: ").strip()
    if confirm != "DELETE EVERYTHING":
        print("❌ Aborted.")
        return

    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            print("Cleaning Users ...")
            # Delete Users first (FK to Org)
            connection.execute(text("DELETE FROM users;"))
            
            print("Cleaning Organizations ...")
            # Delete Organizations
            connection.execute(text("DELETE FROM organizations;"))
            
            # Optional: Reset ID counters (Sequences) so next user is ID 1
            print("Resetting ID counters...")
            connection.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
            connection.execute(text("ALTER SEQUENCE organizations_id_seq RESTART WITH 1;"))
            
            connection.commit()
            print("✅ DONE. Database is clean.")
            print("You must now Register a new admin account immediately.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_db()
