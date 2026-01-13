from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:password@db:5432/ctdirp"
engine = create_engine(DATABASE_URL)

def fix_admin():
    print("Setting admin email...")
    with engine.connect() as conn:
        conn.execute(text("UPDATE users SET email = 'admin@example.com' WHERE username='admin'"))
        conn.commit()
    print("Done. Email: admin@example.com")

if __name__ == "__main__":
    fix_admin()
