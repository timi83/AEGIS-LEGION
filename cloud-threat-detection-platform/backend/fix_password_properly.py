from src.database import SessionLocal
from src.models.user import User
from src.models.audit_log import AuditLog
from passlib.context import CryptContext
from sqlalchemy import text

# Setup Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
new_password = "password123"

# Generate fresh hash
hashed_password = pwd_context.hash(new_password)
print(f"Generated Hash: {hashed_password}")

db = SessionLocal()
try:
    print("Updating password for 'timia'...")
    # Using raw SQL to avoid any ORM validation weirdness, but with a valid generated string
    stmt = text("UPDATE users SET hashed_password = :pwd WHERE username = 'timia'")
    result = db.execute(stmt, {"pwd": hashed_password})
    db.commit()
    print(f"✅ Success. Rows updated: {result.rowcount}")
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
