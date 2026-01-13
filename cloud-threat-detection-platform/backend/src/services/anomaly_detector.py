
import logging
import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from collections import deque

logger = logging.getLogger("ctdirp.ml")
logger.setLevel(logging.INFO)

# Configuration
MODEL_PATH = "model_isolation_forest_v2.pkl" # v2 uses 5 features
TRAINING_BUFFER_SIZE = 100 
ANOMALY_THRESHOLD = -0.6    

class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.buffer = deque(maxlen=TRAINING_BUFFER_SIZE)
        self.is_trained = False
        self.training_mode = True
        
        # Load existing model if available
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.is_trained = True
                self.training_mode = False
                logger.info("🧠 Loaded existing ML model.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")

    def train(self):
        """Train the Isolation Forest model on buffered data."""
        if len(self.buffer) < TRAINING_BUFFER_SIZE:
            return

        logger.info(f"🧠 Training model on {len(self.buffer)} events...")
        try:
            X = np.array(self.buffer)
            self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
            self.model.fit(X)
            
            self.is_trained = True
            self.training_mode = False
            
            # Save model
            joblib.dump(self.model, MODEL_PATH)
            logger.info("✅ Model trained and saved!")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")

    def get_status(self) -> dict:
        """Returns the current status of the ML model."""
        return {
            "mode": "Training" if self.training_mode else "Active",
            "samples": len(self.buffer),
            "required_samples": TRAINING_BUFFER_SIZE,
            "progress": int((len(self.buffer) / TRAINING_BUFFER_SIZE) * 100) if self.training_mode else 100,
            "trained": self.is_trained
        }

    def reset(self):
        """Resets the model to training mode."""
        self.buffer.clear()
        self.model = None
        self.is_trained = False
        self.training_mode = True
        if os.path.exists(MODEL_PATH):
            try:
                os.remove(MODEL_PATH)
                logger.info("🗑️ Deleted ML model file.")
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
                logger.info(f"🧠 Learning... {len(self.buffer)}/{TRAINING_BUFFER_SIZE} samples collected.")
            
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
                    logger.warning(f"🚨 Anomaly Detected! Score: {score:.2f} | Data: {features}")
                    return {
                        "score": float(score),
                        "reason": f"Anomaly Detected (Score: {score:.2f})",
                        "features": {
                            "cpu": cpu, "ram": ram, 
                            "disk_mb": disk, "net_mb": net, "procs": procs
                        }
                    }
            except Exception as e:
                logger.error(f"Inference error (Model Mismatch? Resetting...): {e}")
                self.reset() # Auto-reset if shape mismatch occurs

        return None

# Global instance
detector = AnomalyDetector()

def detect_anomaly(event: dict) -> dict | None:
    return detector.process_event(event)
