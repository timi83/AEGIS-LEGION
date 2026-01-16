
import os
import smtplib
from dotenv import load_dotenv

# Explicitly load .env
load_dotenv()

print("--- DEBUGGING EMAIL CONFIG ---")

email_from = os.getenv("ALERT_EMAIL_FROM")
email_pass = os.getenv("ALERT_EMAIL_PASSWORD")
smtp_server = os.getenv("ALERT_EMAIL_SMTP", "smtp.gmail.com")
port = int(os.getenv("ALERT_EMAIL_PORT", 587))

print(f"EMAIL_FROM: {email_from}")
# Print first 3 chars of password for verification
print(f"EMAIL_PASS: {email_pass[:3] + '***' if email_pass else 'None'}")
print(f"SMTP: {smtp_server}:{port}")

if not email_from or not email_pass:
    print("❌ ERROR: Missing credentials in .env")
    exit(1)

print("\nAttempting to connect to SMTP...")
try:
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    print("✅ STARTTLS success")
    
    print("Attempting login...")
    server.login(email_from, email_pass)
    print("✅ LOGIN success!")
    
    server.quit()
    print("\n🎉 CONCLUSION: Credentials are CORRECT. usage via 'python main.py' should work IF RESTARTED.")
except Exception as e:
    print(f"\n❌ LOGIN FAILED: {e}")
    print("Suggestion: Check if 'Less Secure Apps' is on OR if you need an specific App Password (for Gmail).")
