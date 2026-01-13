import sys
from sqlalchemy import create_engine, text
from src.auth.security import verify_password
from src.database import Base

# DB Connection
DATABASE_URL = "postgresql://postgres:password@db:5432/ctdirp"
engine = create_engine(DATABASE_URL)

def check_logic():
    print("🧪 Checking Logic...")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT hashed_password FROM users WHERE username='admin'"))
        row = res.fetchone()
        if row:
            db_hash = row[0]
            print(f"   DB Hash: {db_hash}")
            is_valid = verify_password("password", db_hash)
            print(f"   verify_password('password', hash) -> {is_valid}")
        else:
            print("   Admin not found")

if __name__ == "__main__":
    check_logic()
