from sqlalchemy import create_engine, text

# DB Connection
DATABASE_URL = "postgresql://postgres:password@db:5432/ctdirp"
engine = create_engine(DATABASE_URL)

def set_plain():
    print("Forcing 'plain:password'...")
    with engine.connect() as conn:
        conn.execute(text("UPDATE users SET hashed_password = 'plain:password' WHERE username='admin'"))
        conn.commit()
    print("Done.")

if __name__ == "__main__":
    set_plain()
