
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base

class IncidentNote(Base):
    __tablename__ = "incident_notes"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Null if system note? Or use System User.
    
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    is_system_log = Column(Boolean, default=False) # e.g. "Status changed to Closed"

    # Relationships
    user = relationship("User", backref="incident_notes")
    incident = relationship("Incident", backref="notes_rel") # "notes" might conflict if Incident defines it
