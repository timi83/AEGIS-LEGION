# src/models/incident.py

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base

# -----------------------------
# INCIDENT MODEL (String-based for stability)
# -----------------------------
class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for now to avoid breaking existing data immediately
    event_id = Column(String(64), unique=True, index=True, nullable=True) # nullable=True for existing data/manual creation compatibility

    # Short title for dashboards
    title = Column(String(255), nullable=False)

    # Multi-Tenancy Scoping
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    org_incident_id = Column(Integer, nullable=True, index=True) # Friendly ID (1, 2, 3...) scoped to Org

    # Source of the incident (e.g., hostname) - Critical for Granular Access Control
    source = Column(String(255), index=True, nullable=True)

    # Longer incident description (why triggered, event source, etc.)
    description = Column(Text, nullable=True)

    # Severity (stored as string: "low", "medium", "high", "critical")
    severity = Column(String(50), nullable=False, default="low")

    # Status (stored as string: "open", "closed", "investigating")
    status = Column(String(50), nullable=False, default="open")

    # Response Notes (Audit trail)
    response_notes = Column(Text, nullable=True, default="")

    # Alert Count (for grouping)
    alert_count = Column(Integer, default=1)

    # When incident was detected
    timestamp = Column(DateTime, default=datetime.utcnow)

    # When incident was updated by IR actions
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Many-to-Many Assignment
    assignees = relationship("src.models.user.User", secondary="incident_assignments", backref="assigned_incidents")

# Association Table Definition being available in metadata
from sqlalchemy import Table
incident_assignments = Table(
    'incident_assignments', Base.metadata,
    Column('incident_id', Integer, ForeignKey('incidents.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    extend_existing=True
)
