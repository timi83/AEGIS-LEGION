
import sys
import os
from sqlalchemy import create_engine, text

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cloud-threat-detection-platform', 'backend'))
from src.database import DATABASE_URL

def check_org(email):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id, username, email, organization, role FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()
        if user:
            print(f"User: {user[1]} | Email: {user[2]} | Org: {user[3]} | Role: {user[4]}")
        else:
            print("User not found")

if __name__ == "__main__":
    check_org("timiabioye11@gmail.com")
