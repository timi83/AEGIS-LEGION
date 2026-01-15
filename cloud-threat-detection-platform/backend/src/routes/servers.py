
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.database import get_db
from src.models.user import User
from src.models.server import Server
from src.routes.auth import get_current_user, get_current_user_by_api_key
from src.auth.permissions import admin_only
from src.services.rule_engine import process_event
from src.services.anomaly_detector import detect_anomaly
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/servers", tags=["Servers"])
# Base path for static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")

class ServerResponse(BaseModel):
    id: int
    name: str | None
    hostname: str
    ip_address: str | None
    os_info: str | None
    # status: str # Replaced by dynamic check in frontend or overridden
    # For now we keep it but it might be stale. 
    # Actually, Pydantic will read the DB 'status' column.
    # To use dynamic, we should use a computed field in Pydantic.
    status: str
    
    cpu_usage: float | None
    ram_usage: float | None
    cpu_usage: float | None
    ram_usage: float | None
    last_heartbeat: datetime | None
    
    # Access Control Check
    allowed_user_ids: List[int] = []

    class Config:
        from_attributes = True

    # Validator removed to trust DB status (updated by heartbeat)
    # If we want dynamic offline, we should do it in the list_servers or frontend
    # but the heartbeat explicitly sets it to 'online' so that should be respected.



class ServerUpdate(BaseModel):
    name: str

class HeartbeatSchema(BaseModel):
    hostname: str
    ip: str
    os: str
    timestamp: float
    status: str
    cpu: Optional[float] = 0.0
    cpu: Optional[float] = 0.0
    ram: Optional[float] = 0.0

from src.services.anomaly_detector import manager

@router.get("/ml/status")
def get_ml_status(user: User = Depends(get_current_user)):
    """Get the current training status of the ML Engine (Scoped to Org)."""
    return manager.get_detector(user.organization_id).get_status()

@router.post("/ml/reset")
def reset_ml_model(user: User = Depends(get_current_user)):
    """Reset the ML model to training mode (Scoped to Org)."""
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can reset the ML brain.")
    
    manager.get_detector(user.organization_id).reset()
    return {"status": f"ML Brain Reset for Org {user.organization_id}"}

@router.get("/agent/download")
def download_agent():
    """Download the official Agent Script."""
    file_path = os.path.join(STATIC_DIR, "agent.py")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Agent script not found")
    return FileResponse(file_path, media_type='application/x-python-code', filename="agent.py")

@router.post("/heartbeat")
def server_heartbeat(
    payload: HeartbeatSchema, 
    user: User = Depends(get_current_user_by_api_key),
    db: Session = Depends(get_db)
):
    """
    Agent Heartbeat.
    Registers server if new (scoped to API Key owner).
    Updates last_heartbeat if existing.
    """
    server = db.query(Server).filter(
        Server.hostname == payload.hostname,
        Server.user_id == user.id
    ).first()
    
    if not server:
        # Register new server
        server = Server(
            hostname=payload.hostname,
            ip_address=payload.ip,
            os_info=payload.os,
            status="online",
            user_id=user.id,
            name=payload.hostname # Default name
        )
        db.add(server)
    else:
        # Update existing
        server.last_heartbeat = datetime.utcnow()
        server.status = "online"
        server.ip_address = payload.ip # Update IP if changed
        
        # Update metrics
        server.cpu_usage = payload.cpu
        server.ram_usage = payload.ram
        server.status = "online" # DB status (informational)
        
    db.commit()
    db.refresh(server)
    
    # -----------------------------------------------
    # 🔍 RULE ENGINE CHECK (Anomaly Detection)
    # -----------------------------------------------
    try:
        # 1. Static Rules (CPU > 90%)
        event_payload = {
            "source": server.hostname,
            "event_type": "system_metric",
            "user_id": user.id,
            "data": {
                "cpu": payload.cpu,
                "ram": payload.ram
            },
            "cpu": payload.cpu,
            "ram": payload.ram
        }
        process_event(event_payload, db)

        # 2. ML Anomaly Detection (Isolation Forest)
        ml_event = {
            "event_type": "system_heartbeat", # detector expects this
            "data": {"cpu": payload.cpu, "ram": payload.ram}
        }
        # Pass Org ID for multi-tenant isolation
        anomaly = detect_anomaly(ml_event, organization_id=user.organization_id)
        
        if anomaly:
            print(f"🧠 ML DETECTED ANOMALY: {anomaly}")
            # Feed back into Rule Engine as an Incident Trigger
            ml_alert_payload = {
                "source": server.hostname,
                "event_type": "ml_anomaly",
                "user_id": user.id,
                "details": anomaly['reason'],
                "score": anomaly['score'],
                "severity": "medium" # ML findings are usually medium until verified
            }
            process_event(ml_alert_payload, db)
            
    except Exception as e:
        print(f"Error in anomaly detection: {e}")

    return {"status": "acknowledged", "server_id": server.id}

@router.get("", response_model=List[ServerResponse])
def list_servers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List servers. Admins see all in Org. Analysts/Viewers see Own + Assigned."""
    
    if current_user.role == 'admin':
        # Admin: See all in Organization
        servers = db.query(Server).join(User).filter(User.organization == current_user.organization).all()
    else:
        # Analyst/Viewer: See Own OR Assigned
        from sqlalchemy import or_
        servers = db.query(Server).filter(
            or_(
                Server.user_id == current_user.id,
                Server.allowed_users.any(id=current_user.id)
            )
        ).all()
        
        
        # ).all() removed
        pass
        
    # Dynamic Status Check & ID Population
    for s in servers:
        s.allowed_user_ids = [u.id for u in s.allowed_users] # Populate for Pydantic
        if s.last_heartbeat and (datetime.utcnow() - s.last_heartbeat).total_seconds() > 90:
            s.status = "offline"
    return servers

class AssignmentPayload(BaseModel):
    user_id: int

@router.post("/{server_id}/assign")
def assign_user_to_server(
    server_id: int, 
    payload: AssignmentPayload,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Assign a user to a specific server (Admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can assign users.")
    
    # Get Server (in Admin's Org)
    server = db.query(Server).join(User).filter(
        Server.id == server_id, 
        User.organization == current_user.organization
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found.")

    # Get Target User (in Admin's Org)
    target_user = db.query(User).filter(
        User.id == payload.user_id,
        User.organization == current_user.organization
    ).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    if target_user not in server.allowed_users:
        server.allowed_users.append(target_user)
        db.commit()
    
    return {"message": f"User {target_user.username} assigned to server {server.name}"}

@router.delete("/{server_id}/assign/{user_id}")
def unassign_user_from_server(
    server_id: int, 
    user_id: int,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Remove user assignment from server."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can unassign users.")
    
    server = db.query(Server).join(User).filter(
        Server.id == server_id, 
        User.organization == current_user.organization
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found.")
        
    target_user = db.query(User).filter(User.id == user_id).first()
    if target_user and target_user in server.allowed_users:
        server.allowed_users.remove(target_user)
        db.commit()
        
    return {"message": "Assignment removed"}

@router.put("/{server_id}", response_model=ServerResponse)
def rename_server(
    server_id: int, 
    payload: ServerUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Rename a server (e.g. 'Accounting DB')."""
    
    if current_user.role in ['admin', 'analyst']:
        # Admin can rename ANY server in their organization
        server = db.query(Server).join(User).filter(
            Server.id == server_id, 
            User.organization == current_user.organization
        ).first()
    else:
        # Viewers can only rename their OWN servers
        server = db.query(Server).filter(Server.id == server_id, Server.user_id == current_user.id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found or access denied")
    
    server.name = payload.name
    db.commit()
    db.refresh(server)
    return server

@router.delete("/{server_id}", dependencies=[Depends(admin_only)])
def delete_server(
    server_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Delete a server (Admin only)."""
    # Admin only (enforced by dependency), so check Organization match
    server = db.query(Server).join(User).filter(
        Server.id == server_id, 
        User.organization == current_user.organization
    ).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    db.delete(server)
    db.commit()
    return {"message": "Server deleted"}
