from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Secret key for JWT encoding/decoding
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

import sys

# Enabling plaintext for recovery in broken environments
# THIS_SHOULD_CRASH_THE_BACKEND_ON_IMPORT (Removed)
sys.stderr.write("DEBUG: security.py module loaded\n")
# NUCLEAR OPTION: Switching to sha256_crypt because bcrypt is incorrectly crashing on length checks in Docker.
pwd_context = CryptContext(schemes=["sha256_crypt", "bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    # print(f"DEBUG: Verifying '{plain_password}' vs '{hashed_password}'") # Reduced log spam
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"DEBUG: CRASH in verify_password: {e}")
        return False

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
