import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "cloud-threat-detection-platform", "backend"))

# Force local DB URL
os.environ["DATABASE_URL"] = "postgresql://postgres:password@localhost:5432/ctdirp"

from src.database import SessionLocal, engine, Base
from src.models.user import User

def check_user():
    # Ensure tables exist
    print("Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Checking for admin user...")
        user = db.query(User).filter(User.username == "admin").first()
        
        from src.auth.security import get_password_hash
        new_hash = get_password_hash("password123")
        
        if user:
            print(f"✅ User 'admin' found (ID: {user.id}). Updating password to 'password123'...")
            user.hashed_password = new_hash
            db.commit()
            print("✅ Password updated.")
        else:
            print("❌ User 'admin' NOT found. Creating with password 'password123'...")
            new_user = User(
                username="admin",
                hashed_password=new_hash
            )
            db.add(new_user)
            db.commit()
            print("✅ Created user 'admin' with password 'password123'")
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
