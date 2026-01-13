
import sys
import os
from sqlalchemy import create_engine, text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from src.database import DATABASE_URL

def migrate_metrics():
    print(f"Connecting to DB: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("Adding cpu_usage column...")
        try:
            connection.execute(text("ALTER TABLE servers ADD COLUMN cpu_usage FLOAT;"))
        except Exception as e:
            print(f"Skipping cpu_usage (maybe exists): {e}")

        print("Adding ram_usage column...")
        try:
            connection.execute(text("ALTER TABLE servers ADD COLUMN ram_usage FLOAT;"))
        except Exception as e:
            print(f"Skipping ram_usage (maybe exists): {e}")
            
        connection.commit()
    
    print("Migration complete.")

if __name__ == "__main__":
    migrate_metrics()
