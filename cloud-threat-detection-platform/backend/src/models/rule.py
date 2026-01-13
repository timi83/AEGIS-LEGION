# backend/src/models/rule.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from src.database import Base
import json

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # conditions is JSON serialized as text — a list of condition dicts:
    # e.g. [{"field":"event_type","op":"equals","value":"login_failed"},
    #       {"field":"data.fail_count","op":"gt","value":3}]
    conditions = Column(Text, nullable=False, default="[]")
    severity = Column(String(50), nullable=False, default="medium")
    enabled = Column(Boolean, nullable=False, default=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Isolation Fields (Nullable for migration, but logic will enforce it)
    organization_id = Column(Integer, nullable=True) # Linked to Organization.id (Logic-enforced FK)
    organization = Column(String(255), nullable=True) # Legacy/Backup string identifier

    def get_conditions(self):
        try:
            return json.loads(self.conditions or "[]")
        except Exception:
            return []
