
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from datetime import datetime
from src.database import Base

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Identification
    name = Column(String, nullable=True) # Friendly name e.g. "Accounting DB"
    hostname = Column(String, index=True)
    ip_address = Column(String, nullable=True)
    os_info = Column(String, nullable=True)
    
    # Real-time Metrics
    cpu_usage = Column(Float, nullable=True)
    ram_usage = Column(Float, nullable=True)
    
    # Health
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="offline") # "online", "offline", "critical"
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Granular Access Control
    # Many-to-Many: Server <-> User (for assignment)
    from sqlalchemy.orm import relationship
    allowed_users = relationship("User", secondary="server_assignments", back_populates="assigned_servers")

from sqlalchemy import Table
# Association Table for Many-to-Many
server_assignments = Table(
    'server_assignments', Base.metadata,
    Column('server_id', Integer, ForeignKey('servers.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)
