import uvicorn
import logging
import sys

# Configure logging to show everything
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if __name__ == "__main__":
    try:
        print("Starting Uvicorn programmatically...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
