import sqlalchemy
from sqlalchemy import create_engine, text
import urllib.parse

# User provided: postgresql://postgres:Rniarns2004!@db.ayrmsijnhvbygqvpcpvd.supabase.co:5432/postgres

password = "Rniarns2004!"
# While ! is usually safe, we will try both raw and encoded if raw fails.
# But logically, we check "Raw" first as that's what the user will paste.
encoded_password = urllib.parse.quote_plus(password) 

host = "db.ayrmsijnhvbygqvpcpvd.supabase.co"
port = "5432"
dbname = "postgres"
user = "postgres"

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
