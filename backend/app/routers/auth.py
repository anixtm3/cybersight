from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.complaint import User, AuditLog
from app.schemas.complaint import LoginRequest, LoginResponse, LogoutRequest
from app.rate_limit import limiter
from app.auth_core import verify_password, create_access_token, revoke_token
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/15minute")
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        audit = AuditLog(
            log_id=uuid.uuid4(),
            action="login",
            target_id=login_data.username,
            ip_address=request.client.host if request.client else "unknown",
            status="FAILED",
        )
        db.add(audit)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # create_access_token embeds sub, role, jurisdiction, bank_name, exp —
    # replaces the old create_token() which only embedded role. This is
    # required for jurisdiction/bank RBAC (auth_core.assert_jurisdiction_access
    # / assert_bank_access) to have anything to check against.
    token = create_access_token(user)

    audit = AuditLog(
        log_id=uuid.uuid4(),
        admin_id=user.id,
        action="login",
        target_id=str(user.id),
        ip_address=request.client.host if request.client else "unknown",
        status="SUCCESS",
    )
    db.add(audit)
    db.commit()

    return LoginResponse(access_token=token, role=user.role)


@router.post("/logout")
def logout(logout_data: LogoutRequest, db: Session = Depends(get_db)):
    # FIX: was `token: str` as a bare param, which FastAPI reads as a query
    # string (?token=...) — the contract documents a JSON body {"token": "..."}.
    # LogoutRequest is a Pydantic model with a single `token: str` field —
    # add it to schemas/complaint.py if it isn't there yet:
    #
    #   class LogoutRequest(BaseModel):
    #       token: str
    #
    # revoke_token() also fixes the missing expires_at: it decodes the JWT's
    # own `exp` claim and stores that, instead of leaving expires_at unset.
    revoke_token(db, logout_data.token)
    return {"message": "Logged out successfully"}