import sys
import os
from sqlalchemy import create_engine, text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))

from src.database import DATABASE_URL

def check_user_email(email):
    print(f"Connecting to DB: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print(f"Checking for user with email: {email}")
        result = connection.execute(text("SELECT id, username, email FROM users WHERE email = :email"), {"email": email})
        user = result.fetchone()
        
        if user:
            print(f"FOUND USER: ID={user[0]}, Username={user[1]}, Email={user[2]}")
        else:
            print("User NOT found.")

if __name__ == "__main__":
    check_user_email("timiabioye11@gmail.com")
