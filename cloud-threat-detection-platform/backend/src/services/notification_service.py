
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
        # SendPulse API Credentials
        "SENDPULSE_ID": os.getenv("SENDPULSE_ID"),
        "SENDPULSE_SECRET": os.getenv("SENDPULSE_SECRET")
    }

# -------------------------------------------------------------------
# EMAIL ALERT
# -------------------------------------------------------------------

import base64

def get_sendpulse_token(user_id, secret):
    """
    Fetches a temporary bearer token from SendPulse (OAuth2).
    """
    url = "https://api.sendpulse.com/oauth/access_token"
    data = {
        "grant_type": "client_credentials",
        "client_id": user_id,
        "client_secret": secret
    }
    try:
        resp = requests.post(url, json=data, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("access_token")
        logger.error(f"❌ SendPulse Token Error ({resp.status_code}): {resp.text}")
        return None
    except Exception as e:
        logger.error(f"❌ SendPulse Auth Exception: {e}")
        return None

def send_via_sendpulse(env, to, subject, html_content):
    """
    Sends email via SendPulse API (HTTP 443).
    Requires 'html' body to be Base64 encoded.
    """
    logger.info(f"🚀 Sending via SendPulse API to {to}...")
    
    # 1. Authenticate
    token = get_sendpulse_token(env["SENDPULSE_ID"], env["SENDPULSE_SECRET"])
    if not token:
        return False
        
    # 2. Prepare Request
    url = "https://api.sendpulse.com/smtp/emails"
    headers = {"Authorization": f"Bearer {token}"}
    
    # SendPulse requires Base64 encoded HTML
    html_b64 = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    
    payload = {
        "email": {
            "subject": subject,
            "html": html_b64,
            "from": {"name": "CTDIRP Platform", "email": env["EMAIL_FROM"] if env["EMAIL_FROM"] else "admin@example.com"},
            "to": [{"email": to}]
        }
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        # SendPulse returns 200 even for some errors, check 'result': true
        if resp.status_code == 200:
            data = resp.json()
            if data.get("result"):
                logger.info(f"✅ SendPulse Success: {data.get('id')}")
                return True
            else:
                logger.error(f"❌ SendPulse API Error: {data}")
                return False
        else:
            logger.error(f"❌ SendPulse Failed ({resp.status_code}): {resp.text}")
            return False
    except Exception as e:
        logger.error(f"❌ SendPulse Connection Error: {e}")
        return False

def send_email_alert(subject: str, body: str, to: str):
    env = get_env_vars()
    
    # PRIORITY 1: Use SendPulse if available
    if env["SENDPULSE_ID"] and env["SENDPULSE_SECRET"]:
        return send_via_sendpulse(env, to, subject, body)

    # PRIORITY 2: Fallback to SMTP
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
        # Resolve to IPv4 specifically
        target_ip = socket.gethostbyname(env['EMAIL_SMTP_SERVER'])
        logger.info(f"🔍 DNS Probe: {env['EMAIL_SMTP_SERVER']} -> {target_ip} (IPv4)")
    except Exception as e:
        logger.error(f"❌ DNS Probe Failed: {e}")
        target_ip = None

    try:
        # Probe Port 587 directly using IPv4 if available
        probe_host = target_ip if target_ip else env['EMAIL_SMTP_SERVER']
        logger.info(f"🔍 Probing Port 587 on {probe_host}...")
        sock = socket.create_connection((probe_host, 587), timeout=5)
        sock.close()
        logger.info("✅ Port 587 Probe: Success (Port is OPEN)")
    except Exception as e:
        logger.error(f"❌ Port 587 Probe Failed: {e} (Port might be BLOCKED)")
        
    try:
        # Check external connectivity
        requests.get("https://www.google.com", timeout=2)
        logger.info("🔍 HTTP Probe: google.com reachable")
    except Exception as e:
        logger.error(f"❌ HTTP Probe Failed (No Internet?): {e}")

    try: 
        # FORCE IPv4 CONNECTION (Bypass potential IPv6 routing issues)
        connect_host = target_ip if target_ip else env["EMAIL_SMTP_SERVER"]
        
        if env["EMAIL_SMTP_PORT"] == 465:
            # SSL Mode
            # Note: server_hostname argument is needed if we connect by IP to verify cert
            import ssl
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(connect_host, env["EMAIL_SMTP_PORT"], timeout=10, context=context)
            # Fix hostname for checks if we used IP
            if target_ip:
                server._host = env["EMAIL_SMTP_SERVER"]
        else:
            # TLS Mode (587)
            server = smtplib.SMTP(connect_host, env["EMAIL_SMTP_PORT"], timeout=10)
            
            # HACK: If we connected via IP, we must restore the hostname BEFORE starttls
            # so that ssl.wrap_socket uses the correct server_hostname for SNI/Cert validation.
            if target_ip:
                logger.info(f"Connected to {target_ip}. Restoring hostname {env['EMAIL_SMTP_SERVER']} for TLS...")
                server._host = env["EMAIL_SMTP_SERVER"]
            
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

    # PRIORITY 1: Use SendPulse if available
    if env["SENDPULSE_ID"] and env["SENDPULSE_SECRET"]:
        logger.info("Redirecting MIME message to SendPulse API...")
        # Extract content from MIME message (Best Effort)
        html_content = None
        subject = msg["Subject"]
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    break
        else:
            html_content = msg.get_payload(decode=True).decode()
            
        if html_content:
            return send_via_sendpulse(env, to_email, subject, html_content)
        else:
            logger.warning("Could not extract HTML from MIME message for SendPulse. Falling back to SMTP.")

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

