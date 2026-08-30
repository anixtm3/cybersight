from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.complaint import MuleAccount, User
from app.routers.complaints import mask_account
from app.auth_core import get_current_user

router = APIRouter(prefix="/api", tags=["mule-accounts"])


# FIX 1: raw account_number was returned for every flagged mule
# account with no masking — now uses the same mask_account() helper
# as complaints.py, for consistency instead of a second implementation.
#
# FIX 2: this endpoint had NO auth dependency at all — anyone hitting
# /api/mule-accounts, logged in or not, got the full registry. Added
# get_current_user() so it now requires a valid JWT, same baseline as
# every other data-returning endpoint in the app. Deliberately NOT
# adding jurisdiction/role filtering here — mule accounts aren't
# scoped to a district the way complaints are, and role-restricting
# this further is a product decision (e.g. "should Bank Nodal Officers
# see mules for banks other than their own?") that needs a team
# answer, not a silent assumption. Flag this back if that's needed
# before the demo.
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
        "geographic_movement": m.geographic_movement
    } for m in mules]