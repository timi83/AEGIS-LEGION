from passlib.context import CryptContext
import sys

try:
    print("Initializing CryptContext with plaintext support...")
    pwd_context = CryptContext(schemes=["bcrypt", "plaintext"], deprecated="auto")
    
    secret = "password123"
    stored_hash = "password123" # Plaintext stored in DB
    
    print(f"Verifying '{secret}' against '{stored_hash}'...")
    result = pwd_context.verify(secret, stored_hash)
    
    if result:
        print("✅ Verification Successful (True)")
    else:
        print("❌ Verification Failed (False)")
        sys.exit(1)

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
