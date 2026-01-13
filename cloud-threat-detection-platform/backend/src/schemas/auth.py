from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    full_name: str | None = None
    organization: str | None = None
    role: str = "viewer" # Default role

class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    role: str | None = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class AuditLogOut(BaseModel):
    id: int
    action: str
    details: str | None
    timestamp: datetime
    username: str

    class Config:
        from_attributes = True
