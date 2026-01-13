import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend')))

from src.database import engine
from sqlalchemy import inspect

def check_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('users')
    col_names = [c['name'] for c in columns]
    print(f"User Table Columns: {col_names}")
    
    if 'created_at' not in col_names:
        print("MISSING: 'created_at' column")
    else:
        print("FOUND: 'created_at' column")

if __name__ == "__main__":
    check_schema()
