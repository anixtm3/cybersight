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


class FlagAccountResponse(BaseModel):
    success: bool
    account_id: str
    tx_hash: str


class CheckAccountResponse(BaseModel):
    blacklisted: bool
    risk_score: int
    flagged_at: int
    reason: str


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

    try:

        tx_hash = flag_mule_account(
            request.account_id,
            request.risk_score,
            request.reason
        )

        return {
            "success": True,
            "account_id": request.account_id,
            "tx_hash": tx_hash
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------------
# GET /api/blockchain/check/{id}
# -----------------------------------

@app.get(
    "/api/blockchain/check/{account_id}",
    response_model=CheckAccountResponse
)
def check_account(
    account_id: str
):

    try:

        # The contract getters expose only the current on-chain state.
        # They do not retain the original flagging transaction hash.
        result = check_blacklist(
            account_id
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
