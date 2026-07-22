from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Secret key for JWT encoding/decoding
SECRET_KEY = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("FATAL ERROR: JWT_SECRET environment variable is missing! Refusing to start to prevent forgery.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# bcrypt is the primary hashing scheme. sha256_crypt is retained only so that
# hashes created before the switch still verify (and get transparently upgraded
# to bcrypt on next login). bcrypt is pinned <4.1 in requirements.txt so passlib
# 1.7.4 can read its version.
pwd_context = CryptContext(schemes=["bcrypt", "sha256_crypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def verify_and_update_password(plain_password, hashed_password):
    """
    Verify a password and, if its hash uses a deprecated scheme (e.g. legacy
    sha256_crypt), return a fresh bcrypt hash to persist — otherwise None.
    Enables transparent migration to bcrypt on login without forcing resets.
    Returns (is_valid: bool, new_hash: str | None).
    """
    try:
        return pwd_context.verify_and_update(plain_password, hashed_password)
    except Exception:
        return False, None

def get_password_hash(password):
    # Bcrypt Limitation: Max 72 bytes.
    encoded = password.encode('utf-8')
    if len(encoded) > 72:
        raise ValueError("Password is too long (Max 72 bytes)")
        
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
