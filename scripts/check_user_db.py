from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:password@localhost:5432/ctdirp"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_users():
    db = SessionLocal()
    try:
        users = db.execute(text("SELECT username, hashed_password, organization FROM users")).fetchall()
        print(f"Found {len(users)} users:")
        for u in users:
            print(f"User: {u[0]}")
            print(f"Org:  {u[2]}")
            print(f"Hash: {u[1]}")
            print("-" * 20)
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
