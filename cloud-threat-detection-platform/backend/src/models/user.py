from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, index=True)
    email = Column(String, unique=True, index=True, nullable=True) # Nullable for migration, but should be required
    full_name = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    hashed_password = Column(String)
    
    # RBAC & Auth
    created_at = Column(DateTime, default=datetime.utcnow)
    
    audit_logs = relationship("AuditLog", back_populates="user")
    role = Column(String, default="admin") # admin, analyst, viewer
    api_key = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)

    # Multi-tenancy V2 (Relational)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    brand_organization = relationship("Organization", back_populates="users")

    # Assigned Servers (Many-to-Many)
    assigned_servers = relationship("Server", secondary="server_assignments", back_populates="allowed_users")
