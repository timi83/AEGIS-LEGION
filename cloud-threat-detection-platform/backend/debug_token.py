from src.auth.security import create_access_token
import sys

try:
    print("Testing Token Generation...")
    token = create_access_token({"sub": "test_user"})
    print(f"✅ Token Generated: {token[:20]}...")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
