from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.complaint import Complaint, Prediction, MoneyRecoveryStatus, MuleAccount
from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from typing import List
import httpx

# ✅ FIX: prefix="/api" added here so every route in this file is
# consistently mounted under /api/... — no more mixing some routes
# with /api and some without.
router = APIRouter(prefix="/api", tags=["complaints"])

BLOCKCHAIN_API = "http://localhost:8001"


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
@router.post("/complaint", response_model=ComplaintResponse)
def create_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    existing = db.query(Complaint).filter(
        Complaint.complaint_id == complaint.complaint_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Complaint ID already exists")

    db_complaint = Complaint(**complaint.model_dump())
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint


# ─── GET /api/complaints (list) — PII masked ─────────────
@router.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(
    alert_level: str = None,
    fraud_type: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)

    if alert_level:
        query = query.filter(Complaint.alert_level == alert_level)
    if fraud_type:
        query = query.filter(Complaint.fraud_type == fraud_type)

    results = query.offset(skip).limit(limit).all()

    # PII Masking
    for c in results:
        if c.mobile_number:
            c.mobile_number = mask_phone(c.mobile_number)
        if c.beneficiary_account:
            c.beneficiary_account = mask_account(c.beneficiary_account)

    return results


# ─── GET /api/complaints/{id} (basic) ────────────────────
@router.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


# ─── GET /api/complaints/{id}/full — X-Admin-Confirm ─────
# ✅ FIX: removed hardcoded "/api" from the route string below.
# It used to be "/api/complaints/{complaint_id}/full" while the
# router itself had no prefix — now that the router prefix is
# "/api", keeping the hardcoded "/api" here would have produced
# "/api/api/complaints/{id}/full" (a duplicate). Route string now
# only needs "/complaints/{id}/full".
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

    # ✅ Blockchain check — NON-BLOCKING
    blockchain_verified = False
    if mule and mule.account_number:
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(
                    f"{BLOCKCHAIN_API}/api/blockchain/check/{mule.account_number}"
                )
                if resp.status_code == 200:
                    blockchain_verified = resp.json().get("blacklisted", False)
        except (httpx.RequestError, Exception):
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

        # ✅ blockchain_verified field added
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
            "amount_withdrawn": float(recovery.amount_withdrawn) if recovery and recovery.amount_lost else None,
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