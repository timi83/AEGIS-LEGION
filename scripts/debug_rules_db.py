import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.models.rule import Rule
from src.database import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ctdirp")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def debug_rules():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT to_regclass('public.rules');"))
            table_exists = result.scalar()
            print(f"Table 'rules' exists: {table_exists}")
            
            if not table_exists:
                print("Creating table...")
                Base.metadata.create_all(bind=engine)
                print("Table created.")
            else:
                print("Table already exists.")
                
            # Try to query
            session = SessionLocal()
            count = session.query(Rule).count()
            print(f"Current rule count: {count}")
            
            # Try to insert
            print("Attempting to insert test rule...")
            rule = Rule(
                name="Debug Rule",
                conditions='[{"field":"test","op":"eq","value":"1"}]',
                severity="low",
                enabled=True
            )
            session.add(rule)
            session.commit()
            print(f"Inserted rule ID: {rule.id}")
            
            # Clean up
            session.delete(rule)
            session.commit()
            print("Deleted debug rule.")
            session.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_rules()
