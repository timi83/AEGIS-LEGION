from src.database import engine
from sqlalchemy import text

print(f"Connecting to: {engine.url}")
try:
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE users CASCADE"))
        connection.commit()
    print("Truncated 'users' table successfully.")
except Exception as e:
    print(f"Error truncating table: {e}")
