from src.database import SessionLocal, engine, Base
from src.models.audit_log import AuditLog
from src.models.organization import Organization
from src.models.user import User
from sqlalchemy import text

def reset_users():
    session = SessionLocal()
    try:
        print("--- DELETING ALL USERS ---")
        num = session.query(User).delete()
        session.commit()
        print(f"✅ Deleted {num} users.")
        
        # Reset ID sequence if Postgres
        try:
             session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
             session.commit()
             print("✅ Sequence reset.")
        except Exception as e:
             print(f"⚠️ Could not reset sequence (sqlite?): {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    reset_users()
