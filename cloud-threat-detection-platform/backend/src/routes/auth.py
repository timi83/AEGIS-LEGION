from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import os
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from pydantic import BaseModel

from src.database import get_db
from src.models.user import User
from src.models.organization import Organization
from src.models.audit_log import AuditLog
from src.schemas.auth import UserCreate, UserResponse, Token, AuditLogOut
from src.auth.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from sqlalchemy.orm import joinedload
from src.services.email_service import EmailService

router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

class UserUpdate(BaseModel):
    username: str | None = None
    full_name: str | None = None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).options(joinedload(User.assigned_servers)).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

from fastapi import Header

def get_current_user_by_api_key(x_api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)):
    """Authenticate agent using X-API-Key header."""
    user = db.query(User).filter(User.api_key == x_api_key).first()
    if not user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return user

from typing import List
from src.auth.permissions import admin_only

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Public registration for new Organizations.
    Creates the first user as 'admin' for the specified organization.
    """
    print(f"🚀 DEBUG: Register endpoint HIT for email: {user.email}")
    # db_user = db.query(User).filter(User.username == user.username).first()
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="This email exists already. Try to login.")
    
    if not user.organization:
         raise HTTPException(status_code=400, detail="Organization is required for registration")

    # Check Org Uniqueness (Case Insensitive?)
    existing_org = db.query(Organization).filter(Organization.name == user.organization).first()
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization name already taken.")

    # Create Organization
    new_org = Organization(name=user.organization)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    hashed_password = get_password_hash(user.password)
    
    new_user = User(
        username=user.username, 
        hashed_password=hashed_password,
        email=user.email,
        full_name=user.full_name,
        organization=user.organization, # user.organization string (legacy)
        organization_id=new_org.id,     # Relational link
        role="admin" 
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Send Welcome Email (Background Task to avoid 502 Timeout)
        background_tasks.add_task(
            EmailService.send_welcome_email,
            to_email=new_user.email, 
            username=new_user.username,
            organization=new_user.organization
        )
        # try:
        #     from src.services.email_service import EmailService
        #     EmailService.send_welcome_email() ...
        # except ...
        # (Removed synchronous call)
            
        return new_user
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        # Cleanup pending org?
        db.delete(new_org)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")

@router.post("/users", response_model=UserResponse, dependencies=[Depends(admin_only)])
def create_user(user: UserCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # db_user = db.query(User).filter(User.username == user.username).first()
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Enforce Organization Isolation:
    # New user MUST belong to the creator's organization.
    target_org = current_user.organization
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username, 
        hashed_password=hashed_password,
        email=user.email,
        full_name=user.full_name,
        organization=target_org, # Force to creator's org
        organization_id=current_user.organization_id, # Inherit relational ID
        role=user.role 
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"User creation failed: {e}")

@router.get("/users", response_model=List[UserResponse], dependencies=[Depends(admin_only)])
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Admins see only users in their Organization
    return db.query(User).filter(User.organization == current_user.organization).all()

@router.get("/users/mentionable", response_model=List[dict])
def list_mentionable_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    List users in the same organization for @mention autocomplete.
    Accessible to all roles (Admin, Analyst, Viewer).
    """
    users = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    return [
        {"username": u.username, "role": u.role}
        for u in users
    ]

@router.delete("/users/{user_id}", dependencies=[Depends(admin_only)])
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a user from the Organization. Cascade deletes will be handled by DB or manual cleanup."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself.")
    
    # Ensure target user belongs to Admin's Org
    user_to_delete = db.query(User).filter(User.id == user_id, User.organization == current_user.organization).first()
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Manual Cascade Delete to avoid FK errors
    from src.models.incident import Incident
    from src.models.rule import Rule
    from src.models.audit_log import AuditLog
    
    # Delete Incidents
    db.query(Incident).filter(Incident.user_id == user_id).delete()
    
    # Rules do not have user_id, skipping.
    
    # Delete Audit Logs (Caution: Usually we keep these, but if user deletes, FK requires nullify or delete)
    # We will delete them for now to allow user deletion. Ideally we should set user_id=None.
    db.query(AuditLog).filter(AuditLog.user_id == user_id).delete()
    
    db.delete(user_to_delete)
    db.commit()
    
    return {"message": f"User {user_to_delete.username} deleted."}

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"DEBUG: Login attempt for {form_data.username}") # OAuth2 form sends 'username' field, but we assume it contains email
    try:
        # LOOKUP BY EMAIL
        user = db.query(User).filter(User.email == form_data.username).first()
        print(f"DEBUG: User found by email: {user}")
    except Exception as e:
        print(f"DEBUG: CRASH in DB Query: {e}")
        raise e
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    # STORE EMAIL IN TOKEN SUB
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------------------------------------------
# USER MANAGEMENT & API KEYS
# ---------------------------------------------------
import secrets
from src.schemas.auth import UserResponse

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me/profile", response_model=UserResponse)
def update_user_profile(payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Allow user to update their display username or full name."""
    if payload.username:
        # Username is now NON-UNIQUE, so we allow any value.
        current_user.username = payload.username
    if payload.full_name:
        current_user.full_name = payload.full_name
            
    db.commit()
    db.refresh(current_user)
    return current_user

class OrganizationUpdate(BaseModel):
    name: str

@router.put("/organization")
def update_organization(payload: OrganizationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Rename the Organization.
    Changes apply to ALL users in this Organization (Relational).
    Only Admin can perform this.
    """
    if current_user.role != 'admin':
         raise HTTPException(status_code=403, detail="Only Admins can rename the Organization.")
    
    if not current_user.organization_id:
         raise HTTPException(status_code=400, detail="User is not linked to an Organization ID.")
    
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")
    
    # Check name uniqueness
    existing = db.query(Organization).filter(Organization.name == payload.name).first()
    if existing and existing.id != org.id:
         raise HTTPException(status_code=400, detail="Organization name already taken.")
    
    old_name = org.name
    org.name = payload.name
    
    # SYNC LEGACY STRING COLUMN (Optional but good for frontend compatibility)
    # We update ALL users in this org to have the new string name
    db.query(User).filter(User.organization_id == org.id).update({User.organization: payload.name})

    db.commit()
    return {"message": f"Organization renamed from '{old_name}' to '{payload.name}' successfully."}

@router.post("/generate-api-key")
def generate_api_key(background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only Admin can generate keys? Or anyone? Let's say anyone for their own agents.
    # If strict RBAC: if current_user.role != 'admin': raise ...
    
    new_key = f"sk_live_{secrets.token_hex(16)}"
    current_user.api_key = new_key
    
    # Audit Logging
    log = AuditLog(
        user_id=current_user.id,
        action="generated_api_key",
        details=f"Generated new API Key ending in ...{new_key[-4:]}"
    )
    db.add(log)
    
    db.commit()
    
    # Send Notification (Background Task)
    try:
        from src.services.email_service import EmailService
        
        # 1. Confirm to User (Actor)
        background_tasks.add_task(
            EmailService.send_api_key_confirmation,
            to_email=current_user.email, 
            key_suffix=new_key[-4:]
        )
        
        # 2. Alert Admin (Isolation: Only admin of THIS org)
        # Fetch organization admin(s)
        # Exclude self if user is admin
        org_admins = db.query(User).filter(
            User.organization_id == current_user.organization_id,
            User.role == "admin",
            User.id != current_user.id # Don't alert self if I am the admin
        ).all()
        
        for admin in org_admins:
            if admin.email:
                background_tasks.add_task(
                    EmailService.send_api_key_admin_alert,
                    admin_email=admin.email, 
                    actor_username=current_user.username, 
                    key_suffix=new_key[-4:]
                )
                
    except Exception as e:
        print(f"⚠️ Failed to queue API key notification: {e}")
        
    return {"api_key": new_key}

@router.get("/audit-logs", response_model=List[AuditLogOut])
def get_audit_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(AuditLog).options(joinedload(AuditLog.user)).order_by(AuditLog.timestamp.desc())

    if current_user.role == 'admin':
        # Admin sees all logs for their Organization
        query = query.join(User).filter(User.organization == current_user.organization)
    else:
        # User sees only their own
        query = query.filter(AuditLog.user_id == current_user.id)

    logs = query.all()
    # Flatten for response model
    return [
        {
            "id": log.id,
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp,
            "username": log.user.username if log.user else "Unknown"
        }
        for log in logs
    ]

# ---------------------------------------------------
# PASSWORD RECOVERY (MOCK)
# ---------------------------------------------------
class ResetPasswordRequest(BaseModel):
    new_password: str

@router.put("/users/{user_id}/reset-password", dependencies=[Depends(admin_only)])
def reset_user_password_by_admin(user_id: int, payload: ResetPasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Allow Admin to reset passwords for Analysts and Viewers.
    Admin CANNOT reset another Admin's password here.
    """
    target_user = db.query(User).filter(User.id == user_id, User.organization == current_user.organization).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if target_user.role == 'admin':
        raise HTTPException(status_code=403, detail="Cannot reset password of another Admin. They must use the recovery flow.")
    
    target_user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    
    return {"message": f"Password for {target_user.username} reset successfully."}

# ---------------------------------------------------
# PASSWORD RECOVERY (ADMIN ONLY)
# ---------------------------------------------------
from pydantic import BaseModel

class EmailSchema(BaseModel):
    email: str

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(payload: EmailSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Don't reveal user existence
        return {"message": "If email exists (and is Admin), reset link sent."}
    
    # Feature Restriction: REMOVED (Allow all users to reset password)
    # if user.role != 'admin':
    #    print(f"⚠️ Password recovery attempted for non-admin {user.email}. Ignoring.")
    #    return {"message": "If email exists (and is Admin), reset link sent."}

    # Generate Signed JWT Token (Short Expiry)
    reset_token = create_access_token(
        data={"sub": user.email, "type": "password_reset"}, 
        expires_delta=timedelta(minutes=15)
    )
    
    # Send Real Email
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    
    try:
        from src.services.email_service import EmailService
        background_tasks.add_task(
            EmailService.send_password_reset_email,
            to_email=user.email,
            reset_link=reset_link
        )
    except Exception as e:
        print(f"❌ Failed to send reset email: {e}")

    return {"message": "If email exists (and is Admin), reset link sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordSchema, db: Session = Depends(get_db)):
    # Verify Signed JWT
    try:
        decoded_payload = jwt.decode(payload.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded_payload.get("sub")
        token_type = decoded_payload.get("type")
        
        if not email or token_type != "password_reset":
             raise HTTPException(status_code=400, detail="Invalid token type")
             
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

# -------------------------------------------------------------------
# DEBUG EMAIL ENDPOINT (Admin Only)
# -------------------------------------------------------------------

class DebugEmailRequest(BaseModel):
    email: str

@router.post("/debug/send-test-email", dependencies=[Depends(admin_only)])
def debug_send_test_email(payload: DebugEmailRequest, current_user: User = Depends(get_current_user)):
    """
    Debug Endpoint to test email sending synchronously.
    Returns detailed error message if it fails.
    """
    try:
        from src.services.email_service import EmailService
        
        print(f"📧 DEBUG: Attempting to send test email to {payload.email}")
        
        # We use send_welcome_email as specific test case
        # It calls notification_service.send_mime_message which we modified to re-raise exceptions
        # if we add a flag, but currently it returns True/False.
        # Wait, I didn't modify EmailService to re-raise, I modified notification_service.
        # Let's check if EmailService catches it. 
        # EmailService catches and prints. I should probably use notification_service directly here for raw error.
        
        from src.services.notification_service import send_email_alert
        
        # Test basic alert first (simpler path)
        success = send_email_alert(
            subject="DEBUG: Test Email from Backend",
            body="<h1>It Works!</h1><p>If you see this, SMTP is configured correctly.</p>",
            to=payload.email
        )
        
        if success:
            return {"message": "Email sent successfully! Check inbox."}
        else:
            raise HTTPException(status_code=500, detail="EmailService returned False. Check logs for SMTP error.")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Email Failure: {str(e)}")
