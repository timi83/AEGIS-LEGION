import sqlalchemy
from sqlalchemy import create_engine, text
import urllib.parse
import socket
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

# Troubleshooting DNS first
try:
    print(f"Resolving {host}...")
    ais = socket.getaddrinfo(host, 5432)
    for result in ais:
        print(f" - Found Address: {result[4]}")
except Exception as e:
    print(f"❌ DNS Resolution Failed: {e}")

encoded_password = urllib.parse.quote_plus(password) # Becomes Rniarns2004%21 probably

print(f"Testing with encoded password: {encoded_password}")

# Construct URI with encoded password
db_url = f"postgresql://postgres:{encoded_password}@{host}:5432/postgres"

try:
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("✅ Connection Successful!")
        print(f"db version: {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
