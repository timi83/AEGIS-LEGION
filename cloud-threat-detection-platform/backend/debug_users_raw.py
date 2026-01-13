from src.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text("SELECT hashed_password FROM users WHERE username = 'timia'"))
    row = result.fetchone()
    if row:
        print(f"HASH_START:{row[0]}:HASH_END")
    print("-------------------------\n")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
