from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.complaint import MuleAccount, User, DispatchLog
from app.routers.complaints import mask_account
from app.auth_core import get_current_user

router = APIRouter(prefix="/api", tags=["mule-accounts"])


@router.get("/mule-accounts")
def get_mule_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mules = db.query(MuleAccount).all()
    return [{
        "account_number": mask_account(m.account_number),
        "account_holder_name": m.account_holder_name,
        "bank_name": m.bank_name,
        "risk_score": m.risk_score,
        "is_red_flagged": m.is_red_flagged,
        "blockchain_tx_hash": m.blockchain_tx_hash,
        "red_flagged_by": m.red_flagged_by,
        "transaction_chain": m.transaction_chain,
        "geographic_movement": m.geographic_movement,
        "red_flagged_at": m.red_flagged_at.isoformat() if m.red_flagged_at else None,
    } for m in mules]


@router.get("/alerts/dispatch-log")
def get_dispatch_log(
    complaint_id: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(DispatchLog)
    if complaint_id:
        query = query.filter(DispatchLog.complaint_id.ilike(f"%{complaint_id}%"))
    if channel:
        query = query.filter(DispatchLog.channel == channel)
    logs = query.order_by(DispatchLog.dispatched_at.desc()).limit(100).all()
    return [{
        "complaint_id": log.complaint_id,
        "channel": log.channel,
        "recipient": log.recipient,
        "dispatched_at": log.dispatched_at.isoformat() if log.dispatched_at else None,
        "delivery_status": log.delivery_status,
        "raw_response": log.raw_response,
    } for log in logs]