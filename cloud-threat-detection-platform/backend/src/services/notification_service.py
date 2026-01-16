# backend/src/services/notification_service.py

import os
import smtplib
from email.mime.text import MIMEText
import requests

# -------------------------------------------------------------------
# Load ENV variables
# -------------------------------------------------------------------

def get_env_vars():
    return {
        "EMAIL_FROM": os.getenv("ALERT_EMAIL_FROM"),
        "EMAIL_PASSWORD": os.getenv("ALERT_EMAIL_PASSWORD"),
        "EMAIL_SMTP_SERVER": os.getenv("ALERT_EMAIL_SMTP", "smtp.gmail.com"),
        "EMAIL_SMTP_PORT": int(os.getenv("ALERT_EMAIL_PORT", 587)),
        "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    }

# -------------------------------------------------------------------
# EMAIL ALERT
# -------------------------------------------------------------------

def send_email_alert(subject: str, body: str, to: str):
    env = get_env_vars()
    if not env["EMAIL_FROM"] or not env["EMAIL_PASSWORD"]:
        print("⚠️ Email alerts disabled (missing credentials). Check ALERT_EMAIL_FROM environment variable.") 
        # Silencing spam logs for now
        return False

    try:
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = env["EMAIL_FROM"]
        msg["To"] = to

        server = smtplib.SMTP(env["EMAIL_SMTP_SERVER"], env["EMAIL_SMTP_PORT"])
        server.starttls()
        server.login(env["EMAIL_FROM"], env["EMAIL_PASSWORD"])
        server.sendmail(env["EMAIL_FROM"], to, msg.as_string())
        server.quit()

        print(f"📧 Email alert sent to {to}")
    except Exception as e:
        print("❌ Email alert error:", e)
        return False

def send_mime_message(msg, to_email):
    """
    Sends a pre-constructed email message (MIMEMultipart or MIMEText) using the configured SMTP settings.
    """
    env = get_env_vars()
    if not env["EMAIL_FROM"] or not env["EMAIL_PASSWORD"]:
        print("⚠️ Email alerts disabled (missing credentials). Check ALERT_EMAIL_FROM environment variable.")
        return False

    try:
        msg["From"] = env["EMAIL_FROM"]
        msg["To"] = to_email

        server = smtplib.SMTP(env["EMAIL_SMTP_SERVER"], env["EMAIL_SMTP_PORT"])
        server.starttls()
        server.login(env["EMAIL_FROM"], env["EMAIL_PASSWORD"])
        server.sendmail(env["EMAIL_FROM"], to_email, msg.as_string())
        server.quit()

        print(f"📧 Email sent to {to_email}")
        return True
    except Exception as e:
        print("❌ SMTP Send Error:", e)
        return False


# -------------------------------------------------------------------
# SLACK ALERT
# -------------------------------------------------------------------

def send_slack_alert(message: str):
    env = get_env_vars()
    if not env["SLACK_WEBHOOK_URL"]:
        # print("⚠️ Slack alerts disabled (no webhook)")
        return False

    try:
        requests.post(env["SLACK_WEBHOOK_URL"], json={"text": message})
        print("💬 Slack alert sent")
        return True
    except Exception as e:
        print("❌ Slack alert error:", e)
        return False

