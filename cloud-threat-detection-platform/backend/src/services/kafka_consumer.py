# backend/src/services/kafka_consumer.py
import json
import os
import time
import logging
import asyncio
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy.orm import Session

# from src.services.rule_engine import RuleEngine # Removed
from src.models.incident import Incident
from src.database import get_db
from src.services.anomaly_detector import detect_anomaly
from src.services.broadcaster import broadcaster
from src.models.user import User
from src.services.email_service import EmailService

logger = logging.getLogger("ctdirp.kafka_consumer")
logger.setLevel(logging.INFO)

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "security-events")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP = os.getenv("KAFKA_GROUP", "ctdirp-group")

def run_anomaly_detector(event: dict, db: Session) -> dict | None:
    """
    Wrapper to call the external anomaly detector service.
    """
    try:
        return detect_anomaly(event)
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return None


def start_consumer(loop_forever=True, max_retries=20, retry_delay=5, main_loop=None):
    """
    Blocking function that attempts to start a Kafka consumer and process messages.
    Designed to be run in a separate thread.
    """
    attempt = 0
    consumer = None

    while attempt < max_retries and consumer is None:
        attempt += 1
        try:
            logger.info(f"Attempting to start Kafka consumer (attempt {attempt}/{max_retries}) -> {KAFKA_BOOTSTRAP}")
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP,
                group_id=KAFKA_GROUP,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True
            )
            logger.info("✅ Kafka consumer connected and listening.")
            break
        except KafkaError as e:
            logger.warning(f"Kafka not available yet: {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
        except Exception as e:
            logger.error("Unexpected error while creating Kafka consumer:", exc_info=True)
            time.sleep(retry_delay)

    if consumer is None:
        logger.error("❌ Failed to connect to Kafka after retries. Consumer not started.")
        return

    # Main consume loop
    try:
        for msg in consumer:
            try:
                event = msg.value
                if event.get("event_type") == "system_heartbeat":
                    logger.debug(f"📥 Received heartbeat: {event}")
                else:
                    logger.info(f"📥 Received event from Kafka: {event}")

                # Obtain DB session (use generator from get_db())
                db = next(get_db())

                # 1. Run rule engine (creates incidents if matched)
                from src.services.rule_engine import process_event
                rule_incidents = process_event(event, db)
                logger.info(f"🔍 Rule engine created incidents: {len(rule_incidents)}")

                # 2. Run optional anomaly detector
                anomaly_result = run_anomaly_detector(event, db)
                if anomaly_result:
                    logger.info(f"⚠️ Anomaly detector flagged: {anomaly_result}")

                # 3. Handle Anomaly & Fallback Incidents
                incident_obj = None # Keep track of created incident for broadcasting
                
                # Check for existing incident for this event_id
                event_id = event.get("event_id")
                
                # If rule engine created incidents, use the first one for broadcast context
                if rule_incidents:
                    # Fetch the actual incident object for the first one
                    first_inc_id = rule_incidents[0]["incident_id"]
                    incident_obj = db.query(Incident).filter(Incident.id == first_inc_id).first()

                if not incident_obj:
                     # Check if we already have an incident for this event (deduplication)
                    if event_id:
                        existing = db.query(Incident).filter(Incident.event_id == event_id).first()
                        if existing:
                            logger.info(f"⚠ Skipping duplicate event_id={event_id}")
                            incident_obj = existing
                    
                    if not incident_obj:
                        if anomaly_result:
                            # create a single incident for anomaly detection result
                            inc = Incident(
                                event_id=event_id,
                                title=f"Anomaly detected",
                                description=f"Anomaly details: {anomaly_result}",
                                severity="high",
                                status="open",
                                user_id=event.get("user_id")
                            )
                            db.add(inc)
                            db.commit()
                            db.refresh(inc)
                            incident_obj = inc
                            logger.info(f"🟠 Created anomaly incident id={inc.id}")

                        # 4. Fallback: Create incident for ALL events (for testing visibility)
                        # Only if no rule matched and no anomaly (and not already created)
                        # EXCLUDE system_heartbeat to prevent spam
                        elif not rule_incidents and event.get("event_type") != "system_heartbeat":
                            from datetime import datetime
                            inc = Incident(
                                event_id=event_id,
                                title=event.get("event_type", "Unknown Event"),
                                description=event.get("details", str(event)),
                                severity=(event.get("severity") or "low").lower(),
                                status="open",
                                timestamp=datetime.utcnow(),
                                user_id=event.get("user_id")
                            )
                            db.add(inc)
                            db.commit()
                            db.refresh(inc)
                            incident_obj = inc
                            logger.info(f"⚪ Created fallback incident id={inc.id}")


                # ---------------------------------------------------------
                # EMAIL ALERT (Critical/High)
                # ---------------------------------------------------------
                if incident_obj and incident_obj.severity in ["critical", "high"]:
                    user_linked = None
                    admin = None
                    try:
                        # 1. Fetch User to get Organization
                        user_linked = db.query(User).filter(User.id == incident_obj.user_id).first()
                        if user_linked and user_linked.organization:
                             # 2. Fetch Admin for Organization
                             admin = db.query(User).filter(User.organization == user_linked.organization, User.role == "admin").first()
                             if admin and admin.email:
                                 EmailService.send_critical_threat_alert(
                                     admin_email=admin.email,
                                     incident_title=incident_obj.title,
                                     incident_id=incident_obj.id,
                                     severity=incident_obj.severity,
                                     organization=user_linked.organization
                                 )
                                 logger.info(f"📧 Sent critical alert to admin {admin.email}")
                    except Exception as e:
                        logger.error(f"Failed to send email alert: {e}")

                db.close()

                # ---------------------------------------------------------
                # BROADCAST TO SSE
                # ---------------------------------------------------------
                # Only broadcast if it's NOT a heartbeat OR if it triggered something
                if event.get("event_type") != "system_heartbeat" or rule_incidents or anomaly_result:
                    payload = {
                        "type": "event",
                        "event": event,
                        "rule_results": [r["title"] for r in rule_incidents] if rule_incidents else None,
                    }
                    
                    if incident_obj:
                        payload["incident"] = {
                            "id": incident_obj.id,
                            "event_id": getattr(incident_obj, "event_id", None),
                            "title": incident_obj.title,
                            "severity": incident_obj.severity,
                            "status": incident_obj.status,
                            "timestamp": incident_obj.timestamp.isoformat() if incident_obj.timestamp else None
                        }

                    if main_loop:
                        asyncio.run_coroutine_threadsafe(broadcaster.publish(payload), main_loop)
                
                else:
                    pass

            except Exception as e:
                logger.exception(f"Error processing Kafka message: {e}")

    except KeyboardInterrupt:
        logger.info("Kafka consumer stopped by KeyboardInterrupt")
    except Exception:
        logger.exception("Kafka consumer stopped unexpectedly")
    finally:
        try:
            consumer.close()
        except Exception:
            pass
        logger.info("Kafka consumer closed")
