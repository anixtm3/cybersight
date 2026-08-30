"""
app/auth_core.py

JWT issuance/verification + jurisdiction- and bank-scoped RBAC.

ASSUMPTIONS FLAGGED (confirm before relying on these):
1. `revoked_tokens` columns confirmed: token_hash, revoked_at, expires_at.
   Revocation is checked by hashing the incoming raw token (SHA-256) and
   looking up token_hash — not by a jti claim.
2. Password hashing assumed to be passlib[bcrypt] — confirm this
   matches whatever auth.py's /login already uses for verification,
   or login and this file will disagree on hash format.
3. SECRET_KEY / ALGORITHM read from environment — set these in .env,
   do not hardcode in source.
"""
from sqlalchemy import text
import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import User

# ── Config ───────────────────────────────────────────────
# NOTE: env var name matches what auth.py already reads (SECRET_KEY).
# The old auth.py had a hardcoded fallback ("fallback-secret-key") —
# removed here on purpose. If SECRET_KEY isn't set, this must crash
# loudly at startup, not silently sign tokens with a public string.
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 8 * 60  # matches auth.py's existing EXPIRE_HOURS = 8

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Canonical role strings — MUST match users.role values in the live DB.
# Do not use the i4c_admin / cybercell_officer naming from the contract's
# [NEW] section until the team confirms a DB-wide rename; using it here
# would silently desync from what /login actually reads from Postgres.
ROLE_ADMIN = "admin"
ROLE_CYBER_CELL_OFFICER = "cyber_cell_officer"
ROLE_BANK_NODAL_OFFICER = "bank_nodal_officer"


# ── Password helpers ─────────────────────────────────────
def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ── Token issuance ───────────────────────────────────────
def create_access_token(user: User) -> str:
    """
    Embeds sub, role, jurisdiction, bank_name (nullable), exp.
    `jurisdiction` claim is derived from users.jurisdiction_district —
    kept as its own claim name per the contract's [NEW] note, even
    though the DB column is named jurisdiction_district.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.username,
        "role": user.role,
        "jurisdiction": user.jurisdiction_district,
        "bank_name": getattr(user, "bank_name", None),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


# ── Token revocation check ───────────────────────────────
def is_token_revoked(db: Session, raw_token: str) -> bool:
    token_hash = _hash_token(raw_token)
    result = db.execute(
        text("SELECT 1 FROM revoked_tokens WHERE token_hash = :h LIMIT 1"), {"h": token_hash}
    ).first()
    return result is not None


def revoke_token(db: Session, raw_token: str):
    """
    Call this from POST /api/auth/logout with the raw token string
    the client sends. expires_at is taken from the token's own `exp`
    claim so a cleanup job can later purge rows past their natural
    expiry instead of keeping the blacklist growing forever.
    """
    token_hash = _hash_token(raw_token)
    try:
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    except JWTError:
        # Token is already invalid/garbled — nothing meaningful to revoke,
        # but don't let logout crash over it.
        expires_at = datetime.now(timezone.utc)

    db.execute(
        text(
            "INSERT INTO revoked_tokens (token_hash, revoked_at, expires_at) "
            "VALUES (:h, now(), :exp) ON CONFLICT DO NOTHING"
        ),
        {"h": token_hash, "exp": expires_at},
    )
    db.commit()


# ── Current-user dependency ──────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if is_token_revoked(db, token):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    # Fetch fresh from DB rather than trusting the JWT claims blindly —
    # if an admin changes someone's role/jurisdiction mid-day, the old
    # token should not keep the stale privilege until it expires.
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
def get_user_from_raw_token(db: Session, raw_token: str) -> User:
    """
    Same validation as get_current_user(), but takes a raw token string
    directly instead of via FastAPI's OAuth2PasswordBearer dependency —
    needed for WebSocket auth, where the token arrives as the first
    JSON message rather than an Authorization header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if is_token_revoked(db, raw_token):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# ── Role-based dependency factory ────────────────────────
def require_role(*allowed_roles: str):
    """
    Usage: current_user: User = Depends(require_role(ROLE_ADMIN, ROLE_CYBER_CELL_OFFICER))
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not permitted for this action",
            )
        return current_user

    return checker


# ── Jurisdiction / bank scoping helpers ──────────────────
def assert_jurisdiction_access(current_user: User, complaint_district: Optional[str]):
    """
    Admin: unrestricted (national view).
    Cyber Cell Officer: must match their own jurisdiction_district.
    Bank Nodal Officer: jurisdiction check does not apply — use
    assert_bank_access instead for that role.
    """
    if current_user.role == ROLE_ADMIN:
        return
    if current_user.role == ROLE_CYBER_CELL_OFFICER:
        if not current_user.jurisdiction_district:
            raise HTTPException(status_code=403, detail="No jurisdiction assigned to this account")
        if complaint_district != current_user.jurisdiction_district:
            raise HTTPException(
                status_code=403,
                detail="This complaint is outside your assigned jurisdiction",
            )
        return
    # Bank nodal officers should never reach this check on a complaint-level
    # jurisdiction filter — if they do, the route wired the wrong dependency.
    raise HTTPException(status_code=403, detail="Not authorized for jurisdiction-scoped access")


def assert_bank_access(current_user: User, beneficiary_bank: Optional[str]):
    """
    Bank Nodal Officer: must match their own bank_name.
    Admin: unrestricted.
    Cyber Cell Officer: not applicable to bank-scoped views.
    """
    if current_user.role == ROLE_ADMIN:
        return
    if current_user.role == ROLE_BANK_NODAL_OFFICER:
        if not current_user.bank_name:
            raise HTTPException(status_code=403, detail="No bank assigned to this account")
        if beneficiary_bank != current_user.bank_name:
            raise HTTPException(
                status_code=403,
                detail="This alert does not belong to your bank",
            )
        return
    raise HTTPException(status_code=403, detail="Not authorized for bank-scoped access")