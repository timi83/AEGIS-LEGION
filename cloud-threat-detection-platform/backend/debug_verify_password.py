from src.database import SessionLocal
from src.models.user import User
from src.models.audit_log import AuditLog
from src.auth.security import verify_password
import sys

db = SessionLocal()
user = db.query(User).filter(User.username == "timia").first()

if not user:
    print("User not found!")
    sys.exit(1)

print(f"User Hash: {user.hashed_password}")

try:
    print("Verifying password 'password123'...")
    is_valid = verify_password("password123", user.hashed_password)
    print(f"✅ Comparison Result: {is_valid}")
except Exception as e:
    print(f"❌ Error during verification: {e}")
    import traceback
    traceback.print_exc()
