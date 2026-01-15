
import logging
import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from collections import deque

logger = logging.getLogger("ctdirp.ml")
logger.setLevel(logging.INFO)

# Configuration

# Configuration
# Configuration
MODEL_DIR = "models"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

TRAINING_BUFFER_SIZE = 100
ANOMALY_THRESHOLD = -0.6

class AnomalyDetector:
    def __init__(self, organization_id: int | str = "global"):
        self.organization_id = organization_id
        # Unique model path per organization
        self.model_path = os.path.join(MODEL_DIR, f"model_org_{organization_id}.pkl")
        
        self.model = None
        self.buffer = deque(maxlen=TRAINING_BUFFER_SIZE)
        self.is_trained = False
        self.training_mode = True
        
        # Load existing model if available
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.is_trained = True
                self.training_mode = False
                logger.info(f"🧠 Loaded existing ML model for Org {organization_id}.")
            except Exception as e:
                logger.error(f"Failed to load model for Org {organization_id}: {e}")

    def train(self):
        """Train the Isolation Forest model on buffered data."""
        if len(self.buffer) < TRAINING_BUFFER_SIZE:
            return

        logger.info(f"🧠 Training model for Org {self.organization_id} on {len(self.buffer)} events...")
        try:
            X = np.array(self.buffer)
            self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
            self.model.fit(X)
            
            self.is_trained = True
            self.training_mode = False
            
            # Save model
            joblib.dump(self.model, self.model_path)
            logger.info(f"✅ Model trained and saved for Org {self.organization_id}!")
            
        except Exception as e:
            logger.error(f"Training failed for Org {self.organization_id}: {e}")

    def get_status(self) -> dict:
        """Returns the current status of the ML model."""
        return {
            "mode": "Training" if self.training_mode else "Active",
            "samples": len(self.buffer),
            "required_samples": TRAINING_BUFFER_SIZE,
            "progress": int((len(self.buffer) / TRAINING_BUFFER_SIZE) * 100) if self.training_mode else 100,
            "trained": self.is_trained,
            "organization_id": self.organization_id
        }

    def reset(self):
        """Resets the model to training mode."""
        self.buffer.clear()
        self.model = None
        self.is_trained = False
        self.training_mode = True
        if os.path.exists(self.model_path):
            try:
                os.remove(self.model_path)
                logger.info(f"🗑️ Deleted ML model file for Org {self.organization_id}.")
            except Exception as e:
                logger.error(f"Failed to delete model file: {e}")
        logger.info("🔄 ML Model Reset to Training Mode.")

    def process_event(self, event: dict) -> dict | None:
        """
        Process a heartbeat event.
        Returns anomaly details if anomalous, else None.
        """
        # Only process system_heartbeat
        if event.get("event_type") != "system_heartbeat":
            return None

        data = event.get("data", {})
        cpu = data.get("cpu")
        ram = data.get("ram")
        disk = data.get("disk_write_mb", 0.0)
        net = data.get("net_out_mb", 0.0)
        procs = data.get("process_count", 0)

        if cpu is None or ram is None:
            return None

        # 5-Dimensional Feature Vector
        features = [cpu, ram, disk, net, procs]

        # 1. Training Phase
        if self.training_mode:
            self.buffer.append(features)
            remaining = TRAINING_BUFFER_SIZE - len(self.buffer)
            if remaining % 10 == 0:
                logger.info(f"🧠 Org {self.organization_id} Learning... {len(self.buffer)}/{TRAINING_BUFFER_SIZE} samples collected.")
            
            if len(self.buffer) >= TRAINING_BUFFER_SIZE:
                self.train()
            
            return None 

        # 2. Inference Phase
        if self.is_trained and self.model:
            try:
                X = np.array([features])
                pred = self.model.predict(X)[0]
                score = self.model.score_samples(X)[0]

                if pred == -1:
                    logger.warning(f"🚨 Org {self.organization_id} Anomaly Detected! Score: {score:.2f} | Data: {features}")
                    return {
                        "score": float(score),
                        "reason": f"Anomaly Detected (Score: {score:.2f})",
                        "features": {
                            "cpu": cpu, "ram": ram, 
                            "disk_mb": disk, "net_mb": net, "procs": procs
                        }
                    }
            except Exception as e:
                logger.error(f"Inference error Org {self.organization_id} (Model Mismatch? Resetting...): {e}")
                self.reset() # Auto-reset if shape mismatch occurs

        return None

# -------------------------------------------------------------------
# Multi-Tenant Manager
# -------------------------------------------------------------------
class OrganizationMLManager:
    def __init__(self):
        self.detectors = {} # { org_id: AnomalyDetector }

    def get_detector(self, organization_id: int | str | None) -> AnomalyDetector:
        # Fallback to "global" if no org ID provided (legacy support)
        key = organization_id if organization_id is not None else "global"
        
        if key not in self.detectors:
            logger.info(f"🆕 Initializing new AnomalyDetector for Org: {key}")
            self.detectors[key] = AnomalyDetector(organization_id=key)
        
        return self.detectors[key]

# Global Singleton Manager
manager = OrganizationMLManager()

def detect_anomaly(event: dict, organization_id: int | str | None = None) -> dict | None:
    # Prefer explicit org_id, then check event dict
    if organization_id is None:
        organization_id = event.get("organization_id")
        
    detector = manager.get_detector(organization_id)
    return detector.process_event(event)

