import sys
try:
    from passlib.context import CryptContext
    print("Passlib imported successfully.")
except ImportError as e:
    print(f"Error importing passlib: {e}")
    sys.exit(1)

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash = pwd_context.hash("testpassword")
    print(f"Hash generated successfully: {hash}")
    verify = pwd_context.verify("testpassword", hash)
    print(f"Verification result: {verify}")
except Exception as e:
    print(f"Error using bcrypt: {e}")
