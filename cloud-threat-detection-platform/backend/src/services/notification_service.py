
import os
import smtplib
import logging
from email.mime.text import MIMEText
import requests
import socket

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        logger.warning("⚠️ Email alerts disabled (missing credentials). Check ALERT_EMAIL_FROM environment variable.") 
        return False

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = env["EMAIL_FROM"]
    msg["To"] = to

    logger.info(f"Attempting valid SMTP send to: {to}")

    # Debug: Print loaded config (masked)
    logger.info(f"SMTP Config: Server={env['EMAIL_SMTP_SERVER']}, Port={env['EMAIL_SMTP_PORT']}")
    
    # NETWORK PROBE
    try:
        ip = socket.gethostbyname(env['EMAIL_SMTP_SERVER'])
        logger.info(f"🔍 DNS Probe: {env['EMAIL_SMTP_SERVER']} -> {ip}")
    except Exception as e:
        logger.error(f"❌ DNS Probe Failed: {e}")
        
    try:
        # Check external connectivity
        requests.get("https://www.google.com", timeout=2)
        logger.info("🔍 HTTP Probe: google.com reachable")
    except Exception as e:
        logger.error(f"❌ HTTP Probe Failed (No Internet?): {e}")

    try: 
        if env["EMAIL_SMTP_PORT"] == 465:
            server = smtplib.SMTP_SSL(env["EMAIL_SMTP_SERVER"], env["EMAIL_SMTP_PORT"], timeout=10)
        else:
            server = smtplib.SMTP(env["EMAIL_SMTP_SERVER"], env["EMAIL_SMTP_PORT"], timeout=10)
            logger.info("Sending STARTTLS command...")
            server.starttls()
            
        server.login(env["EMAIL_FROM"], env["EMAIL_PASSWORD"])
        logger.info("SMTP Login Successful")
        
        server.sendmail(env["EMAIL_FROM"], to, msg.as_string())
        server.quit()

        logger.info(f"📧 Email alert sent to {to}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("❌ SMTP Authentication Failed. Check Username/Password.")
        return False
    except smtplib.SMTPConnectError:
        logger.error("❌ SMTP Connection Failed. Check Server/Port.")
        return False
    except Exception as e:
        logger.error(f"❌ Email alert error: {str(e)}", exc_info=True)
        return False

def send_mime_message(msg, to_email):
    """
    Sends a pre-constructed email message (MIMEMultipart or MIMEText) using the configured SMTP settings.
    """
    env = get_env_vars()
    if not env["EMAIL_FROM"] or not env["EMAIL_PASSWORD"]:
        logger.warning("⚠️ Email alerts disabled (missing credentials). Check ALERT_EMAIL_FROM environment variable.")
        return False

    msg["From"] = env["EMAIL_FROM"]
    msg["To"] = to_email

    logger.info(f"Attempting valid SMTP send to: {to_email}")

    # Debug: Print loaded config (masked)
    logger.info(f"SMTP Config: Server={env['EMAIL_SMTP_SERVER']}, Port={env['EMAIL_SMTP_PORT']}")

    try: 
        if env["EMAIL_SMTP_PORT"] == 465:
            server = smtplib.SMTP_SSL(env["EMAIL_SMTP_SERVER"], env["EMAIL_SMTP_PORT"], timeout=10)
        else:
            server = smtplib.SMTP(env["EMAIL_SMTP_SERVER"], env["EMAIL_SMTP_PORT"], timeout=10)
            logger.info("Sending STARTTLS command...")
            server.starttls()
            
        server.login(env["EMAIL_FROM"], env["EMAIL_PASSWORD"])
        server.sendmail(env["EMAIL_FROM"], to_email, msg.as_string())
        server.quit()

        logger.info(f"📧 Email successfully sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ SMTP Send Error: {str(e)}", exc_info=True)
        raise e # Re-raise so Debug Endpoint can catch it
        # Note: If called from BackgroundTask, this will be logged by FastAPI but won't crash app.


# -------------------------------------------------------------------
# SLACK ALERT
# -------------------------------------------------------------------

def send_slack_alert(message: str):
    env = get_env_vars()
    if not env["SLACK_WEBHOOK_URL"]:
        # logger.debug("⚠️ Slack alerts disabled (no webhook)")
        return False

    try:
        requests.post(env["SLACK_WEBHOOK_URL"], json={"text": message})
        logger.info("💬 Slack alert sent")
        return True
    except Exception as e:
        logger.error(f"❌ Slack alert error: {e}")
        return False

