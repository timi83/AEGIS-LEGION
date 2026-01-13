from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:password@db:5432/ctdirp"
engine = create_engine(DATABASE_URL)

def get_email():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT email, username FROM users WHERE username='admin'"))
        row = res.fetchone()
        if row:
            print(f"Admin: {row[1]}, Email: {row[0]}")
        else:
            print("Admin not found")

if __name__ == "__main__":
    get_email()
