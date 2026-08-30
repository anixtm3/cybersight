from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from blockchain_service import (
    flag_mule_account,
    check_blacklist
)

app = FastAPI(
    title="CyberSight Blockchain API"
)


# -----------------------------------
# REQUEST MODEL
# -----------------------------------

class FlagAccountRequest(BaseModel):
    account_id: str
    risk_score: int
    reason: str
    flagging_authority: str
    evidence_basis: str


# -----------------------------------
# RESPONSE MODELS
# -----------------------------------

class FlagAccountResponse(BaseModel):
    success: bool
    account_id: str
    tx_hash: str | None = None
    block_number: int | None = None
    error: str | None = None


class CheckAccountResponse(BaseModel):
    success: bool
    blacklisted: bool
    risk_score: int | None = None
    flagged_at: int | None = None
    reason: str | None = None
    flagging_authority: str | None = None
    evidence_basis: str | None = None
    account_hash: str | None = None
    error: str | None = None


# -----------------------------------
# POST /api/blockchain/flag
# -----------------------------------

@app.post(
    "/api/blockchain/flag",
    response_model=FlagAccountResponse
)
def flag_account(
    request: FlagAccountRequest
):

    result = flag_mule_account(
        request.account_id,
        request.risk_score,
        request.reason,
        request.flagging_authority,
        request.evidence_basis
    )

    # Blockchain unavailable / transaction failed
    if not result["success"]:
        return {
            "success": False,
            "account_id": request.account_id,
            "tx_hash": None,
            "block_number": None,
            "error": result.get(
                "error",
                "Blockchain operation failed"
            )
        }

    return {
        "success": True,
        "account_id": request.account_id,
        "tx_hash": result["transaction_hash"],
        "block_number": result["block_number"],
        "error": None
    }


# -----------------------------------
# GET /api/blockchain/check/{account_id}
# -----------------------------------

@app.get(
    "/api/blockchain/check/{account_id}",
    response_model=CheckAccountResponse
)
def check_account(
    account_id: str
):

    result = check_blacklist(account_id)

    return result
