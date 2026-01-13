from src.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("Setting plaintext password for 'timia'...") # Emergency Fix
    # Store plain string. Passlib will identify it as 'plaintext' scheme (no prefix usually, or autodetect)
    pwd = "password123"
    stmt = text("UPDATE users SET hashed_password = :pwd WHERE username = 'timia'")
    result = db.execute(stmt, {"pwd": pwd})
    db.commit()
    print(f"✅ Password set to plaintext '{pwd}'.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
