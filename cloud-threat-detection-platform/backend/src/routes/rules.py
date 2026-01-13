# backend/src/routes/rules.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.rule import Rule
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime

router = APIRouter(prefix="/rules", tags=["Rules"])

# DB dependency (keeps consistent with incidents.get_db)
from src.routes.auth import get_current_user
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConditionModel(BaseModel):
    field: str  # dot path like "data.fail_count" or "event_type"
    op: str     # equals, contains, gt, lt
    value: Optional[str] = None

class RuleCreateModel(BaseModel):
    name: str
    description: Optional[str] = None
    conditions: List[ConditionModel]
    severity: Optional[str] = "medium"
    enabled: Optional[bool] = True

@router.post("/", response_model=dict)
def create_rule(payload: RuleCreateModel, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    rule = Rule(
        name=payload.name,
        description=payload.description or "",
        conditions=json.dumps([c.dict() for c in payload.conditions]),
        severity=payload.severity or "medium",
        enabled=payload.enabled,
        created_at=datetime.utcnow(),
        organization_id=current_user.organization_id,
        organization=current_user.organization
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"message": "Rule created", "id": rule.id}

@router.get("/", response_model=List[dict])
def list_rules(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Admin B sees only Org B rules
    rules = db.query(Rule).filter(Rule.organization_id == current_user.organization_id).order_by(Rule.created_at.desc()).all()
    output = []
    for r in rules:
        output.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "conditions": r.get_conditions(),
            "severity": r.severity,
            "enabled": r.enabled,
            "created_at": r.created_at,
        })
    return output

@router.delete("/{rule_id}", response_model=dict)
def delete_rule(rule_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Ensure rule belongs to user's org
    rule = db.query(Rule).filter(Rule.id == rule_id, Rule.organization_id == current_user.organization_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted"}
