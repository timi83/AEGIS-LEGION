from src.database import SessionLocal
from src.models.user import User
from src.auth.security import get_password_hash
import sys

username = "timia"
new_password = "password123"

if len(sys.argv) > 1:
    username = sys.argv[1]

db = SessionLocal()
user = db.query(User).filter(User.username == username).first()

if not user:
    print(f"User {username} not found!")
    sys.exit(1)

print(f"Resetting password for {username}...")
user.hashed_password = get_password_hash(new_password)
db.commit()
print(f"✅ Password for '{username}' has been set to '{new_password}'")

db.close()
