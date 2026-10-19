import hmac
import hashlib
import json
import base64
import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.db.database import get_db
from backend.app.db.models import UserModel

def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode('utf-8'))

def create_access_token(payload: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    exp = int(time.time()) + (expires_delta or settings.access_token_expire_minutes * 60)
    data = {**payload, "exp": exp, "iat": int(time.time())}
    
    header_b64 = _b64_encode(json.dumps(header).encode('utf-8'))
    data_b64 = _b64_encode(json.dumps(data).encode('utf-8'))
    
    signing_input = f"{header_b64}.{data_b64}".encode('utf-8')
    signature = hmac.new(settings.secret_key.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_encode(signature)
    
    return f"{header_b64}.{data_b64}.{sig_b64}"

def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, data_b64, sig_b64 = parts
        
        signing_input = f"{header_b64}.{data_b64}".encode('utf-8')
        expected_sig = hmac.new(settings.secret_key.encode('utf-8'), signing_input, hashlib.sha256).digest()
        actual_sig = _b64_decode(sig_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
            
        payload = json.loads(_b64_decode(data_b64).decode('utf-8'))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None

def get_current_user(request: Request, db: Session = Depends(get_db)) -> UserModel:
    """
    Resolves the authenticated user.
    Supports:
    1. Authorization Bearer JWT Token
    2. Header overrides for local development/demo (`X-User-Role`, `X-User-Email`)
    3. Default employee fallback in demo mode
    """
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    user = None
    if token:
        payload = verify_access_token(token)
        if payload and "user_id" in payload:
            user = db.query(UserModel).filter(UserModel.id == payload["user_id"]).first()

    # Demo / Local dev mock override
    if not user and settings.mock_auth_enabled:
        role = request.headers.get("X-User-Role", "employee").lower()
        email = request.headers.get("X-User-Email", f"{role}@company.internal")
        name = request.headers.get("X-User-Name", f"Demo {role.capitalize()}")
        department = request.headers.get("X-User-Dept", "All")

        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            user = UserModel(
                email=email,
                name=name,
                role=role,
                department=department
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        elif user.role != role or user.department != department:
            user.role = role
            user.department = department
            db.commit()

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required or invalid credentials")

    return user
