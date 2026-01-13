
import sys
import os
from sqlalchemy import create_engine, text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from src.database import DATABASE_URL
from src.auth.security import get_password_hash

def reset_password(email, new_password):
    print(f"Connecting to DB: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    hashed = get_password_hash(new_password)
    
    with engine.connect() as connection:
        print(f"Resetting password for {email}...")
        result = connection.execute(
            text("UPDATE users SET hashed_password = :pwd WHERE email = :email"),
            {"pwd": hashed, "email": email}
        )
        connection.commit()
        print(f"Updated {result.rowcount} rows.")

if __name__ == "__main__":
    reset_password("timiabioye11@gmail.com", "password123")
