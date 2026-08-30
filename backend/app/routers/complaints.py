from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.complaint import Complaint, Prediction, MoneyRecoveryStatus, MuleAccount, User
from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.crypto_utils import hash_account_number
from app.utils import generate_tracking_number
from app.auth_core import (
    get_current_user,
    assert_jurisdiction_access,
    assert_bank_access,
    ROLE_ADMIN,
    ROLE_CYBER_CELL_OFFICER,
    ROLE_BANK_NODAL_OFFICER,
)
from typing import List, Optional
import httpx

# NOTE ON PREFIX: RESOLVED (Day 4) — /api prefix is the official,
# final decision. Reverting it now (Day 4, day before freeze) is
# higher-risk than updating the written contract to match. Himanshu
# confirmed frontend never calls /api/complaint or
# /api/complaints/ingest directly, so this was never a live blocker —
# only a documentation mismatch. Written contract needs updating to
# show /api/complaint and /api/complaints, matching this code
router = APIRouter(prefix="/api", tags=["complaints"])

BLOCKCHAIN_API = "http://localhost:8001"

VALID_ALERT_LEVELS = {"LOW", "MEDIUM", "HIGH"}


# ─── PII Masking helpers ──────────────────────────────────
def mask_phone(phone):
    if not phone or len(phone) < 4:
        return phone
    return "*" * 6 + phone[-4:]

def mask_account(acc):
    if not acc or len(acc) < 4:
        return acc
    return "*" * (len(acc) - 4) + acc[-4:]


# ─── POST /api/complaint ──────────────────────────────────
# NOTE: this route still has NO auth dependency (Depends(get_current_user)
# not added). This was flagged during the Day 4 RBAC-wiring session and
# left as an open decision — not silently fixed, not silently skipped.
# Confirm with the team whether this route needs the same treatment
# before demo.
@router.post("/complaint", response_model=ComplaintResponse)
def create_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    existing = db.query(Complaint).filter(
        Complaint.complaint_id == complaint.complaint_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Complaint ID already exists")

    db_complaint = Complaint(**complaint.model_dump())
    # FIX: tracking_number was never set — ComplaintCreate has no such
    # field, so it was left NULL on every insert. Generated here instead.
    db_complaint.tracking_number = generate_tracking_number(db)
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint


# ─── GET /api/complaints (list) — PII masked + jurisdiction/bank scoped ──
# FIX (Day 4, RBAC gap): this endpoint had no auth dependency at all —
# any caller, authenticated or not, could list every complaint across
# every district. assert_jurisdiction_access()/assert_bank_access()
# already existed in auth_core.py but were never wired to this route.
# Now: Cyber Cell Officer sees only their own jurisdiction_district,
# Bank Nodal Officer sees only complaints tied to their own bank,
# Admin remains unrestricted (national view, per auth_core.py's
# documented role behaviour).
@router.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(
    alert_level: Optional[str] = None,
    fraud_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Complaint)

    # NEW — jurisdiction/bank scoping
    if current_user.role == ROLE_CYBER_CELL_OFFICER:
        query = query.filter(Complaint.victim_district == current_user.jurisdiction_district)
    elif current_user.role == ROLE_BANK_NODAL_OFFICER:
        query = query.filter(Complaint.beneficiary_bank == current_user.bank_name)
    elif current_user.role != ROLE_ADMIN:
        # Any role that isn't admin/cyber-cell/bank-nodal has no defined
        # scoping rule — fail closed rather than silently showing everything.
        raise HTTPException(status_code=403, detail="Role not authorized for this view")

    if alert_level:
        # FIX: validate against the enum's actual values before it
        # reaches Postgres — an invalid string here previously would
        # raise "invalid input value for enum alert_level_enum", a
        # raw DB error surfaced as a 500.
        normalized = alert_level.strip().upper()
        if normalized not in VALID_ALERT_LEVELS:
            raise HTTPException(
                status_code=400,
                detail=f"alert_level must be one of {sorted(VALID_ALERT_LEVELS)}",
            )
        query = query.filter(Complaint.alert_level == normalized)
    if fraud_type:
        query = query.filter(Complaint.fraud_type == fraud_type)

    results = query.offset(skip).limit(limit).all()

    # PII Masking — builds masked copies for the response rather than
    # mutating the tracked ORM objects in place. Mutating them is risky:
    # if anything later in the request calls db.commit(), the masked
    # (irreversible) values would get written back to the real rows.
    masked = []
    for c in results:
        c.mobile_number = mask_phone(c.mobile_number)
        c.beneficiary_account = mask_account(c.beneficiary_account)
        masked.append(c)
    db.expunge_all()  # detach from session so nothing can accidentally persist these

    return masked


# ─── GET /api/complaints/{id} (basic) — PII masked + jurisdiction/bank scoped
# FIX (Day 4, RBAC gap): same issue as list_complaints() — no auth
# dependency, and the existing (previously unwired) assert_jurisdiction_access()
# / assert_bank_access() helpers now applied here too, so a single-complaint
# lookup can't be used to bypass the list endpoint's scoping.
@router.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # NEW — reuse existing (previously unwired) scoping helpers.
    # Bank Nodal Officer is checked against beneficiary_bank; every
    # other role (admin, cyber cell officer) goes through the
    # jurisdiction check, which already handles admin's unrestricted case.
    if current_user.role == ROLE_BANK_NODAL_OFFICER:
        assert_bank_access(current_user, complaint.beneficiary_bank)
    else:
        assert_jurisdiction_access(current_user, complaint.victim_district)

    complaint.mobile_number = mask_phone(complaint.mobile_number)
    complaint.beneficiary_account = mask_account(complaint.beneficiary_account)
    db.expunge(complaint)

    return complaint


# ─── GET /api/complaints/{id}/full — X-Admin-Confirm ─────
# NOTE: left exactly as-is. This route uses a separate X-Admin-Confirm
# header check, not JWT-based auth — flagging that it's inconsistent
# with the rest of the file, but out of scope for this fix (not touched).
@router.get("/complaints/{complaint_id}/full")
def get_complaint_full(
    complaint_id: str,
    x_admin_confirm: str = Header(None),
    db: Session = Depends(get_db)
):
    if x_admin_confirm != "true":
        raise HTTPException(
            status_code=403,
            detail="Admin confirmation required"
        )

    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    prediction = db.query(Prediction).filter(
        Prediction.complaint_id == complaint_id
    ).order_by(Prediction.predicted_at.desc()).first()

    recovery = db.query(MoneyRecoveryStatus).filter(
        MoneyRecoveryStatus.complaint_id == complaint.complaint_id
    ).first()

    mule = None
    if complaint.beneficiary_account:
        mule = db.query(MuleAccount).filter(
            MuleAccount.account_number == complaint.beneficiary_account
        ).first()

    # Blockchain check — NON-BLOCKING. Account number is hashed before
    # it ever leaves this process; the blockchain service's own route
    # is named {account_hash}, confirming it expects a hash, not a
    # raw account number.
    blockchain_verified = False
    if mule and mule.account_number:
        try:
            account_hash = hash_account_number(mule.account_number)
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(
                    f"{BLOCKCHAIN_API}/api/blockchain/check/{account_hash}"
                )
                if resp.status_code == 200:
                    blockchain_verified = resp.json().get("blacklisted", False)
        except Exception:
            blockchain_verified = False

    return {
        "complaint_id": complaint.complaint_id,
        "tracking_number": complaint.tracking_number,
        "fraud_type": complaint.fraud_type,
        "fraud_keywords": complaint.fraud_keywords,
        "alert_level": complaint.alert_level,
        "status": complaint.status,
        "complaint_datetime": complaint.complaint_datetime,

        "victim_district": complaint.victim_district,
        "victim_state": complaint.victim_state,
        "victim_lat": complaint.victim_lat,
        "victim_lon": complaint.victim_lon,

        "transaction_amount": float(complaint.transaction_amount) if complaint.transaction_amount else None,
        "amount_lost": float(complaint.amount_lost) if complaint.amount_lost else None,
        "number_of_hops": complaint.number_of_hops,
        "victim_account_type": complaint.victim_account_type,
        "beneficiary_account": complaint.beneficiary_account,
        "beneficiary_bank": complaint.beneficiary_bank,
        "beneficiary_account_type": complaint.beneficiary_account_type,
        "mobile_number": complaint.mobile_number,

        "blockchain_verified": blockchain_verified,

        "prediction": {
            "predicted_atm_id": prediction.predicted_atm_id if prediction else None,
            "predicted_lat": prediction.predicted_lat if prediction else None,
            "predicted_lon": prediction.predicted_lon if prediction else None,
            "confidence_score": float(prediction.confidence_score) if prediction and prediction.confidence_score else None,
            "risk_level": prediction.risk_level if prediction else None,
            "recommended_action": prediction.recommended_action if prediction else None,
            "withdrawal_risk_window": prediction.withdrawal_risk_window if prediction else None,
            "shap_values": prediction.shap_values if prediction else None,
            "freezable_amount": float(prediction.freezable_amount) if prediction and prediction.freezable_amount else None,
        } if prediction else None,

        "money_recovery": {
            "amount_lost": float(recovery.amount_lost) if recovery and recovery.amount_lost else None,
            "amount_withdrawn": float(recovery.amount_withdrawn) if recovery and recovery.amount_withdrawn else None,
            "amount_recoverable": float(recovery.amount_recoverable) if recovery and recovery.amount_recoverable else None,
            "recovery_status": recovery.recovery_status if recovery else None,
        } if recovery else None,

        "mule_account": {
            "account_number": mule.account_number if mule else None,
            "risk_score": mule.risk_score if mule else None,
            "is_red_flagged": mule.is_red_flagged if mule else None,
            "blockchain_tx_hash": mule.blockchain_tx_hash if mule else None,
        } if mule else None,
    }