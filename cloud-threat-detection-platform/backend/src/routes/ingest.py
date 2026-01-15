from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
import json
import os
from kafka import KafkaProducer
from sqlalchemy.orm import Session
from datetime import datetime

from src.database import get_db
from src.models.user import User
from src.models.server import Server

router = APIRouter(prefix="/ingest", tags=["Ingest"])
from src.services.anomaly_detector import detect_anomaly

# Kafka settings
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "security-events")

producer = None

def get_producer():
    global producer
    if producer is None:
        if os.getenv("KAFKA_ENABLED") != "true":
            return None
            
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                api_version=(0, 10)
            )
        except Exception as e:
            # log error but don't crash app, just disable producer
            print(f"Kafka Producer Initialization Failed: {e}")
            return None
    return producer

from uuid import uuid4

class EventPayload(BaseModel):
    event_id: str | None = None
    source: str
    event_type: str
    details: str | None = None
    severity: str | None = "low"
    data: dict | None = None

    def generate_id(self):
        if not self.event_id:
            self.event_id = str(uuid4())
        return self.event_id

from typing import Optional
from fastapi import Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token", auto_error=False)

from src.routes.auth import get_current_user

async def get_user_for_ingest(
    x_api_key: Optional[str] = Security(api_key_header),
    token: Optional[str] = Security(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # 1. Try API Key
    if x_api_key:
        user = db.query(User).filter(User.api_key == x_api_key).first()
        if user:
            return user
    
    # 2. Try JWT Token (if no API key or invalid)
    if token:
        try:
            return get_current_user(token=token, db=db)
        except:
            pass
            
    raise HTTPException(status_code=401, detail="Missing or Invalid Authentication (API Key or Bearer Token required)")

@router.post("/")
async def ingest_event(
    payload: EventPayload, 
    user: User = Depends(get_user_for_ingest), 
    db: Session = Depends(get_db)
):
    """
    Secure Ingest Endpoint:
    1. Validates X-API-Key.
    2. Updates Server Inventory (Heartbeat).
    3. Sends event to Kafka (tagged with user_id).
    """
    
    # Generate ID if missing
    payload.generate_id()
    event_dict = payload.dict()
    
    # Tag with User ID AND Organization ID (for Rule Isolation)
    event_dict["user_id"] = user.id
    if hasattr(user, "organization_id"):
        event_dict["organization_id"] = user.organization_id
    else:
        # Fallback for old User objects in memory? (Shouldn't happen with fresh fetch)
        event_dict["organization_id"] = None

    # ----------------------------
    # 1) SERVER TRACKING (Asset Inventory)
    # ----------------------------
    if payload.event_type == "system_heartbeat":
        server = db.query(Server).filter(Server.hostname == payload.source, Server.user_id == user.id).first()
        if not server:
            # Register new server
            server = Server(
                user_id=user.id,
                hostname=payload.source,
                name=payload.source, # Default name is hostname
                ip_address=payload.data.get("ip") if payload.data else None,
                os_info=payload.data.get("os") if payload.data else None,
                status="online",
                last_heartbeat=datetime.utcnow()
            )
            db.add(server)
        else:
            # Update existing
            server.last_heartbeat = datetime.utcnow()
            server.status = "online"
            if payload.data:
                if payload.data.get("ip"): server.ip_address = payload.data.get("ip")
                if payload.data.get("os"): server.os_info = payload.data.get("os")
        
        db.commit()

    # ----------------------------
    # 1.5) ML ANOMALY DETECTION
    # ----------------------------
    if payload.event_type == "system_heartbeat":
        try:
            # Pass dictionary representation to detector with ORG CONTEXT
            anomaly = detect_anomaly(event_dict, organization_id=user.organization_id)
            
            if anomaly:
                print(f"🧠 ML DETECTED ANOMALY: {anomaly}")
                # Feed back into Rule Engine as an Incident Trigger
                ml_alert_payload = {
                    "source": payload.source,
                    "event_type": "ml_anomaly",
                    "user_id": user.id,
                    "organization_id": user.organization_id, # PASS ORG ID
                    "details": anomaly['reason'],
                    "score": anomaly['score'],
                    "severity": "medium", # ML findings are usually medium until verified
                    "data": anomaly['features']
                }
                # Process this new anomaly event immediately
                # (Note: This might create a second broadcast, which is fine)
                from src.services.rule_engine import process_event as process_rule_event
                process_rule_event(ml_alert_payload, db)

        except Exception as e:
            print(f"Error in anomaly detection pipeline: {e}")

# ----------------------------
    # 2) DIRECT PROCESSING (No Kafka)
    # ----------------------------
    try:
        # Import internally to avoid circular deps if any, 
        # though rule_engine shouldn't import ingest.
        from src.services.rule_engine import process_event
        
        # Process directly (Synchronous)
        results = process_event(event_dict, db)
        
        # Optional: Broadcast to Frontend via SSE (if main.py supports it easily, 
        # but rule_engine usually returns results. 
        # For simplicity in this "Direct Mode", we verify specific logic in rule_engine.
        # Note: The original Kafka consumer also did broadcasting. 
        # Ideally, `process_event` should just return results, and WE handle broadcasting here.
        # But let's check if rule_engine does broadcasting? 
        # Checking previous file view... rule_engine returns a list of result dicts.
        # It does NOT broadcast. The Kafka consumer did the broadcasting.
        
        # We should probably add a simple broadcast here if we want the frontend to see it live.
        # Let's import the broadcaster.
        from src.services.broadcaster import broadcaster
        import asyncio
        
        # We need the main loop to broadcast? 
        # In a route handler (async), we can just await broadcaster.publish()!
        # Much simpler than the thread hack in consumer.
        
        sse_payload = {
            "type": "event",
            "event": event_dict,
            "rule_results": [r["title"] for r in results] if results else None
        }
        
        # If an incident was created/merged, we should try to include it.
        # The rule_engine returns a list of result dicts that contain "incident": object.
        # Let's pick the first one for the payload if it exists.
        if results:
            inc_data = results[0].get("incident")
            if inc_data:
                # inc_data is the ORM object in rule_engine.py
                sse_payload["incident"] = {
                    "id": inc_data.id,
                    "title": inc_data.title,
                    "severity": inc_data.severity,
                    "status": inc_data.status,
                    "timestamp": inc_data.timestamp.isoformat() if inc_data.timestamp else None
                }
        
        # Fire and forget broadcast (or await if fast)
        await broadcaster.publish(sse_payload)
            
    except Exception as e:
        # Log but don't fail the request 500 if rule engine crashes, 
        # though for direct ingestion, maybe we should?
        # Let's return 500 so user knows it failed.
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")

    return {
        "status": "ok",
        "message": "Event ingested successfully",
        "event_id": payload.event_id
    }
