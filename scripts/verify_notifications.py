# scripts/verify_notifications.py
import sys
import os

# Add backend to path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend'))

from src.services.notification_service import send_email_alert, send_telegram_alert
from dotenv import load_dotenv

# Load env from backend
env_path = os.path.join(os.path.dirname(__file__), '../cloud-threat-detection-platform/backend/.env')
load_dotenv(env_path)

print("----------------------------------------------------------------")
print("📧 TESTING EMAIL ALERT...")
print(f"From: {os.getenv('ALERT_EMAIL_FROM')}")
print(f"To: {os.getenv('ALERT_EMAIL_TO')}")
email_success = send_email_alert(
    subject="[TEST] Direct Verification",
    body="This is a direct test from the verification script.",
    to=os.getenv("ALERT_EMAIL_TO")
)
print(f"Result: {'✅ Success' if email_success else '❌ Failed'}")

print("\n----------------------------------------------------------------")
print("📲 TESTING TELEGRAM ALERT...")
print(f"Chat ID: {os.getenv('TELEGRAM_CHAT_ID')}")
telegram_success = send_telegram_alert("This is a direct test from the verification script.")
print(f"Result: {'✅ Success' if telegram_success else '❌ Failed'}")
print("----------------------------------------------------------------")
