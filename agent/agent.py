
import time
try:
    import psutil
except ImportError:
    psutil = None
import requests
import random
import platform
import socket
import logging

# Configuration
API_URL = "http://127.0.0.1:8001/api"
import os

# ---------------------------------------------------------
# 🔑 CONFIGURATION
# ---------------------------------------------------------
# Get API Key from Environment Variable or Paste below
API_KEY = os.getenv("AGENT_API_KEY", "REPLACE_WITH_YOUR_GENERATED_KEY") 
# ---------------------------------------------------------

SOURCE_NAME = socket.gethostname()
OS_INFO = f"{platform.system()} {platform.release()}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("agent")

def send_event(event_type, details, severity="low", data=None):
    """Send a security event to the platform using API Key."""
    headers = {"X-API-Key": API_KEY}
    payload = {
        "source": SOURCE_NAME,
        "event_type": event_type,
        "details": details,
        "severity": severity,
        "data": data or {}
    }
    
    try:
        # Add IP address to data if not present
        if data is None: data = {}
        if "ip" not in data:
            try:
                data["ip"] = socket.gethostbyname(socket.gethostname())
            except:
                pass
        if "os" not in data:
            data["os"] = OS_INFO
            
        payload["data"] = data

        res = requests.post(f"{API_URL}/ingest/", json=payload, headers=headers, timeout=5)
        if res.status_code == 200:
            logger.info(f"Sent event: {event_type} ({severity})")
        elif res.status_code == 401:
             logger.error("❌ Authentication Failed: Invalid API Key. Please check your configuration.")
        else:
            logger.warning(f"Failed to send event: {res.status_code} {res.text}")
    except Exception as e:
        logger.error(f"Error sending event: {e}")

import threading

def heartbeat_loop():
    """Runs every 10 seconds to send vital signs."""
    logger.info("❤️  Heartbeat thread started (Interval: 10s)")
    
    last_disk_io = psutil.disk_io_counters() if psutil else None
    last_net_io = psutil.net_io_counters() if psutil else None
    last_time = time.time() - 10 # Force first run logic valid

    while True:
        try:
            current_time = time.time()
            dt = current_time - last_time
            if dt < 1: dt = 1 
            
            # 1. Collect System Stats
            if psutil:
                # Non-blocking CPU check (interval=None) for instant reading since we sleep manually
                # Or use interval=1 but we want 10s cycle? 
                # Better: interval=None, then we sleep for 10s.
                cpu_usage = psutil.cpu_percent(interval=None) 
                ram_usage = psutil.virtual_memory().percent
                
                disk_io = psutil.disk_io_counters()
                disk_write_mb = 0.0
                if last_disk_io:
                     write_bytes = disk_io.write_bytes - last_disk_io.write_bytes
                     disk_write_mb = (write_bytes / 1024 / 1024) / dt
                last_disk_io = disk_io

                net_io = psutil.net_io_counters()
                net_out_mb = 0.0
                if last_net_io:
                    sent_bytes = net_io.bytes_sent - last_net_io.bytes_sent
                    net_out_mb = (sent_bytes / 1024 / 1024) / dt
                last_net_io = net_io

                process_count = len(psutil.pids())

            else:
                # Mock data
                cpu_usage = random.randint(10, 30)
                ram_usage = random.randint(40, 60)
                disk_write_mb = random.uniform(0.1, 5.0)
                net_out_mb = random.uniform(0.01, 2.0)
                process_count = random.randint(100, 200)

            # Send Heartbeat
            logger.info(f"❤️  Heartbeat: CPU={cpu_usage}% RAM={ram_usage}%")
            send_event("system_heartbeat", f"Stats: CPU {cpu_usage}% | RAM {ram_usage}%", "low", {
                "cpu": cpu_usage,
                "ram": ram_usage,
                "disk_write_mb": disk_write_mb,
                "net_out_mb": net_out_mb,
                "process_count": process_count,
                "os": OS_INFO
            })

            last_time = current_time
            time.sleep(10) # Wait 10s for next heartbeat

        except Exception as e:
            logger.error(f"Heartbeat loop error: {e}")
            time.sleep(10)

def monitor_loop():
    """Runs every 1 second to check for threats (Simulation)."""
    logger.info("🛡️  Monitor thread started (Interval: 1s)")
    while True:
        try:
            # ---------------------------------------------------------
            # 2. THREAT SIMULATION (Independent of Heartbeat)
            # ---------------------------------------------------------
            
            # 10% chance to simulate a failed login
            if random.random() < 0.1:
                send_event("login_failed", "Failed login attempt detected", "medium", {
                    "fail_count": random.randint(1, 5),
                    "user": "admin"
                })

            # 1% chance to simulate a CRITICAL malware event
            if random.random() < 0.01:
                send_event("malware_detected", "Suspicious process detected: miner.exe", "high", {
                    "path": "/tmp/miner.exe",
                    "hash": "badhash123"
                })
            
            time.sleep(1) # Fast checking cycle

        except Exception as e:
            logger.error(f"Monitor loop error: {e}")
            time.sleep(5)

def run_agent():
    logger.info(f"Starting Agent on {SOURCE_NAME} ({OS_INFO})...")
    logger.info(f"Target Backend: {API_URL}")
    
    if API_KEY == "REPLACE_WITH_YOUR_GENERATED_KEY":
        logger.warning("⚠️  WARNING: No API Key configured!")

    if psutil:
         # Prime CPU usage (requires one call to set baseline)
         psutil.cpu_percent(interval=None)

    # Start Threads
    t1 = threading.Thread(target=heartbeat_loop, daemon=True)
    t2 = threading.Thread(target=monitor_loop, daemon=True)
    
    t1.start()
    t2.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Agent stopped by user.")
