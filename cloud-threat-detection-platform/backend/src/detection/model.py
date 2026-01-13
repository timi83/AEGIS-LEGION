import math
from .rules import simple_rule_check

class Detector:
    """Very small placeholder detector. Replace with ML models or more advanced logic."""
    def __init__(self):
        # Example thresholds / config
        self.score_threshold = 0.7

    def run(self, event: dict) -> dict:
        # A toy anomaly score based on numeric fields if present
        score = 0.0
        reasons = []

        # Rule based check (example)
        rule_flag, rule_reason = simple_rule_check(event)
        if rule_flag:
            reasons.append(rule_reason)
            score = max(score, 0.95)

        # Numeric heuristic: look for a field called 'value' or 'size'
        for k in ('value','size','bytes'):
            if k in event and isinstance(event[k], (int, float)):
                # normalize with a simple function
                val = float(event[k])
                score_candidate = 1 - math.exp(-val/1000.0)
                if score_candidate > score:
                    score = score_candidate
                    reasons.append(f"high_{k}")

        anomaly = score >= self.score_threshold
        return {"score": round(score, 3), "anomaly": anomaly, "reasons": reasons}
