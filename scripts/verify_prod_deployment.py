
import requests
import sys

URL = "https://aegis-legion.onrender.com"

def check_cors():
    print(f"🔍 Checking Headers for {URL}...")
    try:
        # Check Health first
        resp = requests.get(f"{URL}/api/health", timeout=10)
        print(f"✅ Health Check Status: {resp.status_code}")
        
        # Check OPTIONS (Preflight) for CORS
        # We simulate a request from Vercel
        headers = {
            "Origin": "https://aegis-legion-f1mbsp52h-timis-projects-227381e3.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
        res_opt = requests.options(f"{URL}/api/incidents", headers=headers, timeout=10)
        
        print("\n--- CORS HEADERS (OPTIONS Request) ---")
        print(f"Status: {res_opt.status_code}")
        cors_origin = res_opt.headers.get("Access-Control-Allow-Origin")
        cors_creds = res_opt.headers.get("Access-Control-Allow-Credentials")
        
        print(f"Access-Control-Allow-Origin: {cors_origin}")
        print(f"Access-Control-Allow-Credentials: {cors_creds}")
        
        if cors_origin == "*" and not cors_creds:
             print("\n✅ SUCCESS: New 'Allow All' policy is ACTIVE.")
        elif cors_creds == 'true':
             print("\n⚠️  WARNING: Old 'Allow Credentials' policy might still be active.")
             if cors_origin != "*":
                  print(f"   Current Allowed Origin: {cors_origin}")
        else:
             print("\n❓ UNKNOWN STATE.")

    except Exception as e:
        print(f"\n❌ REQUEST FAILED: {e}")

if __name__ == "__main__":
    check_cors()
