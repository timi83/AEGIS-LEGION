from src.database import engine
from sqlalchemy import text

print(f"Connecting to: {engine.url}")
try:
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS rules"))
        connection.commit()
    print("Dropped 'rules' table successfully.")
except Exception as e:
    print(f"Error dropping table: {e}")
