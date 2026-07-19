import sqlalchemy
from sqlalchemy import create_engine, text
import urllib.parse
import os
import sys

# Load credentials from environment variables
password = os.getenv("SUPABASE_PASSWORD")
host = os.getenv("SUPABASE_HOST")

if not password or not host:
    print("❌ Error: SUPABASE_PASSWORD and SUPABASE_HOST environment variables are not set.")
    print("Please set them before running the script, e.g.:")
    print("  $env:SUPABASE_PASSWORD=\"your_password\"")
    print("  $env:SUPABASE_HOST=\"your_host_address\"")
    sys.exit(1)

# While ! is usually safe, we will try both raw and encoded if raw fails.
# But logically, we check "Raw" first as that's what the user will paste.
encoded_password = urllib.parse.quote_plus(password) 

port = os.getenv("SUPABASE_PORT", "5432")
dbname = os.getenv("SUPABASE_DB", "postgres")
user = os.getenv("SUPABASE_USER", "postgres")

# Construct URI 
db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

print(f"Testing connection to: {host}...")

try:
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("✅ Connection Successful!")
        print(f"db version: {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    
    print("\nAttempting with URL encoding...")
    try:
        db_url_enc = f"postgresql://{user}:{encoded_password}@{host}:{port}/{dbname}"
        engine2 = create_engine(db_url_enc)
        with engine2.connect() as conn2:
            conn2.execute(text("SELECT 1"))
            print("✅ Connection Successful using URL ENCODING!")
            print(f"Recommended Connection String: {db_url_enc}")
    except Exception as e2:
        print(f"❌ Retry Failed: {e2}")
