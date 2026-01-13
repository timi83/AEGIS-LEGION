from src.database import SessionLocal
from src.models.user import User
from src.models.audit_log import AuditLog
from src.models.server import Server

db = SessionLocal()
users = db.query(User).all()

print(f"Found {len(users)} users in the database:")
for user in users:
    print(f"ID: {user.id} | Username: {user.username} | Email: {user.email} | Organization: {user.organization}")
    
db.close()
