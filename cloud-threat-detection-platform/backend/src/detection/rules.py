# src/detection/rules.py

def apply_rule_engine(event: dict):
    """
    Very basic rule engine. This will later be replaced
    or combined with your ML anomaly detection model.
    """

    # Example Rule 1 — Multiple failed logins
    if event.get("event_type") == "login_failed" and event.get("count", 0) > 5:
        return {
            "is_threat": True,
            "description": "Multiple failed login attempts detected.",
            "severity": "medium"
        }

    # Example Rule 2 — Suspicious root access
    if event.get("user") == "root" and event.get("action") == "unauthorized_access":
        return {
            "is_threat": True,
            "description": "Unauthorized root access.",
            "severity": "high"
        }

    # Default — No threat
    return {
        "is_threat": False,
        "description": "No suspicious activity detected.",
        "severity": "none"
    }
