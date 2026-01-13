from src.database import SessionLocal
from sqlalchemy import text

username = "timia"
# Hash for "password123" extracted from API
hashed_password = "$2b$12$ZfZUqeCZ9ywVZv4DYTVi7lw2wmUuXI8W3xYf27AZ"

db = SessionLocal()
try:
    print(f"Renaming 'string' to '{username}' and resetting password...")
    stmt = text("UPDATE users SET username = :new_user, hashed_password = :pwd WHERE username = 'string'")
    result = db.execute(stmt, {"pwd": hashed_password, "new_user": username})
    
    if result.rowcount == 0:
        print("User 'string' not found. Trying to update 'timia' directly...")
        stmt = text("UPDATE users SET hashed_password = :pwd WHERE username = :user")
        result = db.execute(stmt, {"pwd": hashed_password, "user": username})

    print(f"Updated {result.rowcount} rows.")
    
    print("Cleaning up temp_user...")
    db.execute(text("DELETE FROM users WHERE username = 'temp_user'"))
    
    db.commit()
    print("✅ Success. Password set to 'password123'")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
