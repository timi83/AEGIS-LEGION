    
import requests
import random
import time
import sys
import json

# Configuration
API_URL = "http://localhost:8000/api"
API_KEY = "your_api_key_here" # Placeholder
HOSTNAME = "ml-simulation-01"

def get_admin_token():
    # Login as admin to check incidents later
    try:
        resp = requests.post(f"{API_URL}/token", data={"username": "admin@example.com", "password": "securepassword"})
        if resp.status_code == 200:
            return resp.json()["access_token"]
        print("⚠️ Could not log in as admin. Defaulting to assuming success if no crashes.")
        return None
    except:
        return None

def run_simulation():
    print(f"🚀 Starting ML Simulation on {HOSTNAME}...")
    print("1️⃣  Phase 1: Training the Model (Sending 105 normal heartbeats)...")
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    # Train with "Normal" data: CPU between 10% and 15%
    for i in range(105):
        payload = {
            "hostname": HOSTNAME,
            "ip": "192.168.1.50",
            "os": "Linux/ Simulator",
            "timestamp": time.time(),
            "status": "online",
            "cpu": random.uniform(10.0, 15.0), # NORMAL behavior
            "ram": random.uniform(30.0, 35.0)
        }
        try:
            resp = requests.post(f"{API_URL}/servers/heartbeat", json=payload, headers=headers)
            sys.stdout.write(f"\r   Sent {i+1}/105 | CPU: {payload['cpu']:.1f}% ")
            sys.stdout.flush()
        except Exception as e:
            print(f"\n❌ Connection failed: {e}")
            return

    print("\n✅ Training Complete. Model should now be live.")
    
    # Small pause to ensure backend processed training
    time.sleep(2)
    
    print("2️⃣  Phase 2: The Anomaly (Sending CPU 55%)...")
    # Note: 55% is NOT > 90% (Static Rule), so only ML should catch this.
    
    payload = {
        "hostname": HOSTNAME,
        "ip": "192.168.1.50",
        "os": "Linux/ Simulator",
        "timestamp": time.time(),
        "status": "online",
        "cpu": 65.5, # ANOMALY for this server (normally 12%)
        "ram": 32.0 
    }
    requests.post(f"{API_URL}/servers/heartbeat", json=payload, headers=headers)
    print("   Anomaly Sent!")

    print("3️⃣  Phase 3: Verifying Incident Creation...")
    token = get_admin_token()
    if token:
        # Check audit logs or incidents
        # Since we don't have a direct "get incident by hostname" public API easily handy without admin, 
        # we will check the recent audit logs or list incidents.
        headers_admin = {"Authorization": f"Bearer {token}"}
        
        # Give it a second to process
        time.sleep(2)
        
        try:
            # We implemented listing incidents? Let's try searching or just checking logs
            # Actually, let's assume if we get here, we check the console output of the backend or trust the dashboard.
            # But let's try to hit /api/audit-logs
            res = requests.get(f"{API_URL}/audit-logs", headers=headers_admin)
            logs = res.json()
            found = False
            for log in logs:
                if "ML Anomaly" in str(log.get("details", "")) or "Isolation Forest" in str(log.get("details", "")):
                    print(f"✅ CONFIRMED: Found Audit Log for ML Anomaly: {log['details']}")
                    found = True
                    break
            
            if not found:
                 print("⚠️ No Audit Log found yet. Check Dashboard Incidents.")
                 
        except Exception as e:
            print(f"Could not verify via API: {e}")
    else:
        print("ℹ️  Please check your Dashboard for an Incident titled 'ML Anomaly'.")

if __name__ == "__main__":
    run_simulation()
