
import requests
import time
import concurrent.futures

BASE_URL = "http://127.0.0.1:8000/api"

def make_request(i):
    try:
        # Hit a lightweight endpoint
        resp = requests.get(f"{BASE_URL}/health")
        return resp.status_code
    except Exception as e:
        return f"Error: {e}"

def test_rate_limit():
    print("🚀 Testing Rate Limiting...")
    print("Sending 200 requests rapidly...")
    
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request, i) for i in range(200)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    duration = time.time() - start_time
    print(f"Done in {duration:.2f}s")
    
    success = results.count(200)
    throttled = results.count(429)
    errors = len(results) - success - throttled
    
    print(f"✅ Success (200): {success}")
    print(f"🛑 Throttled (429): {throttled}")
    print(f"⚠️ Errors: {errors}")
    
    if throttled > 0:
        print("\n✅ Rate Limiting is EFFECTIVE!")
    else:
        print("\n❌ Rate Limiting NOT DETECTED (or limit is too high)")

if __name__ == "__main__":
    test_rate_limit()
