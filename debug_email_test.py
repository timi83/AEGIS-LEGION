import sys
import os

# 1. Setup Environment (Mocking what main.py does)
from dotenv import load_dotenv
load_dotenv(dotenv_path="cloud-threat-detection-platform/backend/.env")

# 2. Add backend to path so imports work
# We need to point to .../backend so that 'from src...' works
backend_path = os.path.join(os.getcwd(), 'cloud-threat-detection-platform', 'backend')
sys.path.append(backend_path)
print(f"DEBUG: Added {backend_path} to sys.path")

# 3. Import Email Service
try:
    from backend.src.services.email_service import EmailService
except ImportError:
    # Fallback if running from inside backend dir
    sys.path.append(os.getcwd())
    from src.services.email_service import EmailService

# 4. Test Configuration
TEST_EMAIL = "timiabioye11@gmail.com" # Default from .env or user provided
if len(sys.argv) > 1:
    TEST_EMAIL = sys.argv[1]

print(f"--- STARTING EMAIL TEST TO: {TEST_EMAIL} ---")

# 5. Check Env
pw = os.getenv("ALERT_EMAIL_PASSWORD")
print(f"DEBUG: Password found length: {len(pw) if pw else 0}")
if not pw or "PLACEHOLDER" in pw:
    print("❌ ERROR: Real Password missing in .env")
    sys.exit(1)

# 6. Send
try:
    print("Attempting to send welcome email...")
    success = EmailService.send_welcome_email(
        to_email=TEST_EMAIL,
        username="TestUser",
        organization="Debug Corp"
    )
    
    if success:
        print("\n✅ SUCCESS: Email sent (captured in logs or sent via SMTP).")
        print("Check your inbox (and SPAM folder).")
    else:
        print("\n❌ FAILURE: EmailService returned False.")

except Exception as e:
    print(f"\n❌ CRASH: {e}")
    import traceback
    traceback.print_exc()
