
import sys
import os
from sqlalchemy import create_engine, text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from src.database import DATABASE_URL

def migrate_remove_unique_username():
    print(f"Connecting to DB: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("Checking for unique constraints on username...")
        
        # Postgres specific: Drop the unique index/constraint
        # The index name is usually 'ix_users_username' or 'users_username_key'
        # based on SQLAlchemy defaults.
        
        drop_index_sql = "DROP INDEX IF EXISTS ix_users_username;"
        drop_constraint_sql = "ALTER TABLE users DROP CONSTRAINT IF EXISTS users_username_key;"
        
        try:
            print("Attempting to drop unique index 'ix_users_username'...")
            connection.execute(text(drop_index_sql))
            print("Dropped index (if existed).")
        except Exception as e:
            print(f"Index drop warning: {e}")

        try:
            print("Attempting to drop constraint 'users_username_key'...")
            connection.execute(text(drop_constraint_sql))
            print("Dropped constraint (if existed).")
        except Exception as e:
            print(f"Constraint drop warning (might not exist): {e}")

        connection.commit()
    
    print("Migration complete. Username should now be non-unique.")

if __name__ == "__main__":
    migrate_remove_unique_username()
