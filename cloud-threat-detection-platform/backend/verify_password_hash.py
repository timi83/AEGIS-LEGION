from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# DB Connection
DATABASE_URL = "postgresql://postgres:password@db:5432/ctdirp"
engine = create_engine(DATABASE_URL)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check():
    print("🔍 Checking Admin Password Hash...")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT hashed_password FROM users WHERE username='admin'"))
        row = res.fetchone()
        if not row:
            print("❌ Admin user not found!")
            return
        
        db_hash = row[0]
        print(f"   DB Hash: {db_hash}")
        
        # Verify
        try:
            valid = pwd_context.verify("password", db_hash)
            print(f"   Verify('password'): {valid}")
        except Exception as e:
            print(f"❌ Verify crashed: {e}")

        # If invalid/crashed, generate NEW valid hash
        if not valid:
            print("⚠️ Hash invalid. Generating NEW hash using local passlib...")
            new_hash = pwd_context.hash("password")
            print(f"   New Hash: {new_hash}")
            
            conn.execute(text("UPDATE users SET hashed_password = :h WHERE username='admin'"), {"h": new_hash})
            conn.commit()
            print("✅ Admin password reset to 'password' with VALID hash.")

if __name__ == "__main__":
    check()
