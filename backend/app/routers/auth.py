from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.complaint import User, RevokedToken, AuditLog
from app.schemas.complaint import LoginRequest, LoginResponse
from app.rate_limit import limiter
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import hashlib
import os
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM = "HS256"
EXPIRE_HOURS = 8


def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=EXPIRE_HOURS)
    data.update({"exp": expire, "role": "admin"})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/15minute")
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    # ✅ username se query
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not pwd_context.verify(login_data.password, user.password_hash):
        audit = AuditLog(
            log_id=uuid.uuid4(),
            action="login",
            target_id=login_data.username,
            ip_address=request.client.host if request.client else "unknown",
            status="FAILED"
        )
        db.add(audit)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_token({"sub": user.username})

    audit = AuditLog(
        log_id=uuid.uuid4(),
        admin_id=user.id,
        action="login",
        target_id=str(user.id),
        ip_address=request.client.host if request.client else "unknown",
        status="SUCCESS"
    )
    db.add(audit)
    db.commit()

    return LoginResponse(access_token=token)


@router.post("/logout")
def logout(token: str, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    revoked = RevokedToken(
        token_hash=token_hash,
        revoked_at=datetime.utcnow()
    )
    db.add(revoked)
    db.commit()

    return {"message": "Logged out successfully"}