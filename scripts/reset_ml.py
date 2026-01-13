
import os
import requests

MODEL_PATH = "cloud-threat-detection-platform/backend/model_isolation_forest.pkl"

if os.path.exists(MODEL_PATH):
    os.remove(MODEL_PATH)
    print("✅ ML Brain Deleted (Reset).")
else:
    print("ℹ️  No ML Brain found (already reset).")

# Optional: Restart backend trigger? 
# In dev mode (uvicorn --reload), touching a file might trigger reload, but deleting a .pkl won't.
# We might need to restart just to clear the in-memory 'detector' instance.
print("👉 PLEASE RESTART YOUR BACKEND SERVER for changes to take effect.")
print("   (Ctrl+C in the terminal and run it again)")
