# backend/src/services/rule_engine.py

import logging
from typing import Any, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    from src.models.rule import Rule
except Exception:
    Rule = None

from src.models.incident import Incident


# ---------------------------------------------------------
# 🔥 Incident lookup / merge logic
# ---------------------------------------------------------

def _find_existing_incident(db: Session, source: str, event_type: str, user_id: int):
    """
    Looks for an existing OPEN incident for the same source + event_type + user_id.
    Returns the incident object or None.
    """
    try:
        logger.info(f"Searching for existing incident: source={source}, event_type={event_type}, user_id={user_id}")
        query = db.query(Incident).filter(
            Incident.status == "Open",
            Incident.title.ilike(f"%{event_type}%"),
            Incident.description.ilike(f"%{source}%"),
            Incident.user_id == user_id
        )
        incident = query.first()
        logger.info(f"Found existing incident: {incident.id if incident else 'None'}")
        return incident
    except Exception as e:
        logger.exception("Error searching for existing incident: %s", e)
        return None


def _update_existing_incident(db: Session, incident: Incident, event: dict, new_severity: str = None):
    """
    Update existing incident instead of creating a new one.
    """
    try:
        # increase alert count
        if not hasattr(incident, "alert_count"):
            incident.alert_count = 1  

        incident.alert_count = (incident.alert_count or 1) + 1

        # update description with last event summary
        incident.description = (
            incident.description
            + f"\n[+] Additional event at {datetime.utcnow()} → {event}"
        )

        incident.updated_at = datetime.utcnow()
        
        # Priority Override System: Upgrade severity if specific rule is higher
        if new_severity:
            levels = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            current_level = levels.get(incident.severity.lower() if incident.severity else "low", 0)
            new_level = levels.get(new_severity.lower(), 0)
            if new_level > current_level:
                incident.severity = new_severity
                logger.info(f"Upgraded incident severity to {new_severity} via overriding rule")
                
        db.commit()
        db.refresh(incident)

        logger.info("Merged event into existing incident id=%s", incident.id)

        return {
            "id": incident.id,
            "merged": True,
            "alert_count": incident.alert_count,
            "title": incident.title,
            "severity": incident.severity,
            "incident": incident # Return full object for kafka consumer compatibility
        }

    except Exception as e:
        logger.exception("Failed to update existing incident: %s", e)
        db.rollback()
        return {"error": str(e)}



# ---------------------------------------------------------
# 🔥 Create NEW incident (fallback)
# ---------------------------------------------------------

def _create_incident(db: Session, title: str, description: str, severity: str, user_id: int, source: str = None, status="Open"):
    try:
        # Resolve Organization ID from User
        from src.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        org_id = user.organization_id if user else None
        
        # Calculate next scoped ID
        next_id = 1
        if org_id:
            last_inc = db.query(Incident).filter(Incident.organization_id == org_id).order_by(Incident.org_incident_id.desc()).first()
            if last_inc and last_inc.org_incident_id:
                next_id = last_inc.org_incident_id + 1

        inc = Incident(
            title=title,
            description=description,
            severity=severity,
            status=status,
            timestamp=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            alert_count=1,
            user_id=user_id,
            organization_id=org_id,
            org_incident_id=next_id,
            source=source
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        logger.info("Created NEW incident id=%s for user_id=%s source=%s", inc.id, user_id, source)
        return {
            "id": inc.id, 
            "merged": False,
            "title": inc.title,
            "severity": inc.severity,
            "incident": inc # Return full object for kafka consumer compatibility
        }
    except Exception as e:
        logger.exception("Error creating incident: %s", e)
        db.rollback()
        return {"error": str(e)}



# ---------------------------------------------------------
# 🔥 Rule matching logic (same as Step 8)
# ---------------------------------------------------------

def _event_matches_simple_rule(event: dict, rule: dict) -> bool:
    try:
        # Support existing "field/op/value" format (list of conditions)
        if isinstance(rule, list):
            for cond in rule:
                field = cond.get("field")
                op = cond.get("op")
                val = cond.get("value")
                
                keys = field.split(".")
                actual = event
                for part in keys:
                    if isinstance(actual, dict) and part in actual:
                        actual = actual[part]
                    else:
                        actual = None
                        break
                
                if op == "equals":
                    if str(actual) != str(val): 
                        print(f"DEBUG: Rule mismatch: {field} ({actual}) != {val}", flush=True)
                        return False
                elif op == "contains":
                    if str(val) not in str(actual): return False
                elif op == "gt":
                    try:
                        if not (float(actual) > float(val)): 
                            print(f"DEBUG: Rule mismatch: {field} ({actual}) not > {val}", flush=True)
                            return False
                    except: return False
                elif op == "lt":
                    try:
                        if not (float(actual) < float(val)): return False
                    except: return False
                
                print(f"✅ DEBUG: Rule Condition Matched: {field} ({actual}) {op} {val}", flush=True)
            return True

        if "event_type" in rule:
            if event.get("event_type") != rule["event_type"]:
                return False

        for k, cond in rule.items():
            if k == "event_type":
                continue

            keys = k.split(".")
            val = event
            for part in keys:
                if isinstance(val, dict) and part in val:
                    val = val[part]
                else:
                    val = None
                    break

            # simple equality
            if not isinstance(cond, dict):
                if val != cond:
                    return False
            else:
                # operator comparison
                for op, target in cond.items():
                    try:
                        vnum = float(val)
                        tnum = float(target)
                    except Exception:
                        vnum = val
                        tnum = target

                    if op == ">" and not (vnum > tnum): return False
                    if op == "<" and not (vnum < tnum): return False
                    if op in (">=",) and not (vnum >= tnum): return False
                    if op in ("<=",) and not (vnum <= tnum): return False
                    if op in ("==","=") and not (vnum == tnum): return False

        return True

    except Exception:
        return False



# ---------------------------------------------------------
# 🔥 Main processing entrypoint
# ---------------------------------------------------------

def process_event(event: dict, db: Session) -> List[Dict[str, Any]]:
    logger.info("Processing event: %s", event)
    print(f"🔍 DEBUG: processing event: {event.get('event_type')}", flush=True)
    results = []

    # extract these for grouping logic
    source = event.get("source")
    event_type = event.get("event_type")
    user_id = event.get("user_id") # Extracted from event

    # -----------------------------------------------------
    # 1) Try DB rules first (if Rule model exists)
    # -----------------------------------------------------
    if Rule:
        try:
            # MULTI-TENANT ISOLATION LOGIC
            # Only fetch rules that match the event's organization
            organization_id = event.get("organization_id")
            
            query = db.query(Rule).filter(getattr(Rule, "enabled", True) == True)
            
            if organization_id is not None:
                # Isolate: Rules must match Org
                query = query.filter(Rule.organization_id == organization_id)
                from sqlalchemy import or_
                query = query.filter(or_(Rule.target_server == None, Rule.target_server == source))
                print(f"🔍 DEBUG: Fetching rules for Org ID: {organization_id}", flush=True)
            else:
                # Legacy/Global fallback
                query = query.filter(Rule.organization_id == None)
                print(f"🔍 DEBUG: Fetching GLOBAL rules (No Org ID in event)", flush=True)

            rules = query.all()
            # Priority Sorting: Targeted rules (not None) evaluated FIRST
            rules.sort(key=lambda r: getattr(r, "target_server", None) is None)
            
            print(f"🔍 DEBUG: Found {len(rules)} active rules for this context", flush=True)

            for r in rules:
                cond = getattr(r, "condition", None) or getattr(r, "conditions", None) or getattr(r, "definition", None)
                if isinstance(cond, str):
                    import json
                    try:
                        cond = json.loads(cond)
                    except: pass

                if (isinstance(cond, dict) or isinstance(cond, list)) and _event_matches_simple_rule(event, cond):
                    print(f"✅ DEBUG: Rule '{r.name}' MATCHED event!", flush=True)
                    # if match → perform merge or create new
                    existing = _find_existing_incident(db, source, event_type, user_id)

                    if existing:
                        result = _update_existing_incident(db, existing, event, new_severity=getattr(r, "severity", None))
                        results.append({
                            "rule_id": r.id, 
                            "merged": True, 
                            "incident_id": result["id"],
                            "title": result["title"],
                            "severity": result["severity"],
                            "incident": result["incident"]
                        })
                    else:
                        title = r.name or f"Match: {r.id}"
                        desc = f"Rule matched. Event: {event}"
                        result = _create_incident(db, title, desc, r.severity or "low", user_id, source=source)
                        results.append({
                            "rule_id": r.id, 
                            "merged": False, 
                            "incident_id": result["id"],
                            "title": result["title"],
                            "severity": result["severity"],
                            "incident": result["incident"]
                        })
            
            if results:
                return results

        except Exception as e:
            logger.exception("DB rule engine error: %s", e)


    # -----------------------------------------------------
    # 2) FALLBACK RULES (no DB rules)
    # -----------------------------------------------------

    # Example 0: Manual Test (Frontend Button)
    if event_type in ("manual_test", "quick_test"):
        title = "Test Incident"
        desc = f"Manual test event triggered from {source}. Details: {event.get('details')}"
        res = _create_incident(db, title, desc, "low", user_id, source=source)
        results.append({
            "rule": "manual_test_rule",
            "incident_id": res["id"],
            "title": res["title"],
            "severity": res["severity"],
            "incident": res["incident"]
        })

    # Example 1: brute force login
    if event_type == "login_failed":
        fail_count = event.get("data", {}).get("fail_count", 0)
        if fail_count >= 3:

            existing = _find_existing_incident(db, source, event_type, user_id)

            if existing:
                res = _update_existing_incident(db, existing, event)
                results.append({
                    "rule": "fallback_login_failed",
                    "incident_id": res["id"],
                    "title": res["title"],
                    "severity": res["severity"],
                    "incident": res["incident"]
                })
            else:
                title = "Brute-force login_failed attempt"
                desc = f"Source {source} repeated failures: {fail_count}"
                res = _create_incident(db, title, desc, "high", user_id, source=source)
                results.append({
                    "rule": "fallback_login_failed",
                    "incident_id": res["id"],
                    "title": res["title"],
                    "severity": res["severity"],
                    "incident": res["incident"]
                })

    # Example 2: critical event types
    if event_type in ("malware_detected", "ransomware_activity", "privilege_escalation"):
        existing = _find_existing_incident(db, source, event_type, user_id)

        if existing:
            res = _update_existing_incident(db, existing, event)
            if "error" in res:
                logger.error(f"Failed to update incident: {res['error']}")
            else:
                results.append({
                    "rule": "fallback_critical",
                    "incident_id": res["id"],
                    "title": res["title"],
                    "severity": res["severity"],
                    "incident": res["incident"]
                })
        else:
            title = f"Critical Alert: {event_type}"
            desc = f"Detected {event_type} from {source}. Details: {event.get('details', 'No details')}"
            severity = "high"
            res = _create_incident(db, title, desc, severity, user_id, source=source)
            if "error" in res:
                logger.error(f"Failed to create incident: {res['error']}")
            else:
                results.append({
                    "rule": "fallback_critical",
                    "incident_id": res["id"],
                    "title": res["title"],
                    "severity": res["severity"],
                    "incident": res["incident"]
                })

    # Example 3: ML Anomaly
    if event_type == "ml_anomaly":
        existing = _find_existing_incident(db, source, "ml_anomaly", user_id)
        severity = event.get("severity", "medium")
        
        if existing:
            res = _update_existing_incident(db, existing, event)
        else:
            title = f"ML Anomaly: {source}"
            desc = f"Unusual behavior detected: {event.get('details')} (Score: {event.get('score')})"
            res = _create_incident(db, title, desc, severity, user_id, source=source)

        results.append({
            "rule": "ml_isolation_forest",
            "incident_id": res["id"],
            "title": res["title"],
            "severity": res["severity"],
            "incident": res["incident"]
        })

    return results
