
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from src.database import Base
from sqlalchemy.orm import relationship

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, index=True) # e.g. "generated_api_key"
    details = Column(String, nullable=True) # e.g. "API Key terminated in ...A123"
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
