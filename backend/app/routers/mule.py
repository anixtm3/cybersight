from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.complaint import MuleAccount

router = APIRouter(prefix="/api", tags=["mule-accounts"])


@router.get("/mule-accounts")
def get_mule_accounts(db: Session = Depends(get_db)):
    mules = db.query(MuleAccount).all()
    return [{
        "account_number": m.account_number,
        "account_holder_name": m.account_holder_name,
        "bank_name": m.bank_name,
        "risk_score": m.risk_score,
        "is_red_flagged": m.is_red_flagged,
        "blockchain_tx_hash": m.blockchain_tx_hash,
        "red_flagged_by": m.red_flagged_by,
        "transaction_chain": m.transaction_chain,
        "geographic_movement": m.geographic_movement
    } for m in mules]