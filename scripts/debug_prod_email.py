import requests
import getpass
import sys

def main():
    print("--- Production Email Debugger ---")
    print("This script will log in to your PRODUCTION backend and trigger the test email.")
    
    # 1. Get Config
    base_url = input("Enter Production API URL (e.g. https://yourapp.onrender.com): ").strip()
    if not base_url:
        print("URL required.")
        return
        
    # Remove trailing slash
    if base_url.endswith("/"):
        base_url = base_url[:-1]
        

    
    # 2. Auth Credentials
    print("\n--- Authentication ---")
    email = input("Admin Email: ").strip()
    password = getpass.getpass("Admin Password: ").strip()
    
    # 3. Get Token
    token_url = f"{base_url}/api/token"
    print(f"\nLogging in via {token_url}...")
    
    try:
        # OAuth2 form data
        resp = requests.post(token_url, data={"username": email, "password": password})
        
        if resp.status_code != 200:
            print(f"❌ Login Failed! Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            return
            
        token_data = resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            print("❌ No access_token returned!")
            return
            
        print("✅ Login Successful. Token acquired.")
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 4. Send Debug Email
    print("\n--- Send Test Email ---")
    target_email = input("Target Email Address (to receive test): ").strip()
    
    # CORRECTED URL: /api/debug/send-test-email (removed /auth)
    debug_url = f"{base_url}/api/debug/send-test-email"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to {debug_url}...")
    
    try:
        resp = requests.post(debug_url, json={"email": target_email}, headers=headers)
        
        print("\n--- SERVER RESPONSE ---")
        print(f"Status Code: {resp.status_code}")
        try:
            print(f"Body: {resp.json()}")
        except:
            print(f"Body: {resp.text}")
            
        if resp.status_code == 200:
            print("\n✅ SUCCESS! The email was sent via SMTP.")
        else:
            print("\n❌ FAILURE! Read the error details above to debug SMTP settings.")
            
    except Exception as e:
        print(f"❌ Request Error: {e}")

if __name__ == "__main__":
    main()
