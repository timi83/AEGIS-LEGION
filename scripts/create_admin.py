import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend')))

from src.database import SessionLocal
from src.models.user import User
from src.auth.security import get_password_hash

def create_admin(username, password, email):
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User '{username}' already exists.")
            return

        hashed_pw = get_password_hash(password)
        new_admin = User(
            username=username,
            hashed_password=hashed_pw,
            email=email,
            role="admin",
            full_name="System Administrator",
            organization="Internal"
        )
        db.add(new_admin)
        db.commit()
        print(f"✅ Admin user '{username}' created successfully!")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("--- Create Admin User ---")
    if len(sys.path) < 2:
        # Ensure backend is in path (already done at top, but good practice)
        pass

    if len(sys.argv) == 4:
        # Non-interactive mode: python create_admin.py <username> <email> <password>
        u = sys.argv[1]
        e = sys.argv[2]
        p = sys.argv[3]
        create_admin(u, p, e)
    else:
        # Interactive mode
        try:
            u = input("Username: ")
            e = input("Email: ")
            p = input("Password: ")
            create_admin(u, p, e)
        except KeyboardInterrupt:
            print("\nCancelled.")
