"""
app/web3_service.py

Thin wrapper around the deployed MuleAccountRegistry contract.
Intended for Aniket's /api/blockchain/flag, /check, /proof endpoints —
this is a starting scaffold, not a replacement for his own service
design. Review/adjust with him before wiring it into real routes,
especially around error handling for a down/unreachable Ganache node
(the plan requires blockchain calls to be non-blocking with a timeout —
this file doesn't add that itself; the calling endpoint should wrap
these functions in a try/except with a short timeout, same pattern
already used in complaints.py's blockchain check).

REQUIRES: scripts/deploy_contract.py has been run at least once, so
contracts/deployed_address.json exists.
"""

import json
from pathlib import Path

from web3 import Web3

GANACHE_URL = "http://127.0.0.1:8545"  # match scripts/deploy_contract.py
DEPLOYED_INFO_PATH = Path(__file__).resolve().parent.parent / "contracts" / "deployed_address.json"

if not DEPLOYED_INFO_PATH.exists():
    raise FileNotFoundError(
        f"{DEPLOYED_INFO_PATH} not found — run `python -m scripts.deploy_contract` first"
    )

with open(DEPLOYED_INFO_PATH) as f:
    _deployed = json.load(f)

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
contract = w3.eth.contract(address=_deployed["address"], abi=_deployed["abi"])
w3.eth.default_account = w3.eth.accounts[0]

# Must match the enum order in MuleAccountRegistry.sol exactly —
# Solidity enums are positional, not named, on the wire.
EVIDENCE_BASIS_MAP = {
    "COMPLAINT_PATTERN": 0,
    "BANK_REPORT": 1,
    "LEA_INVESTIGATION": 2,
    "ML_PREDICTION": 3,
    "MANUAL_REVIEW": 4,
}
EVIDENCE_BASIS_REVERSE = {v: k for k, v in EVIDENCE_BASIS_MAP.items()}


def flag_account(account_hash_hex: str, authority: str, evidence_basis: str, risk_score: int, reason: str) -> str:
    """
    account_hash_hex: 64-char hex string — the output of
    app.crypto_utils.hash_account_number(), NOT a raw account number.
    Returns the transaction hash as a hex string.
    """
    account_hash_bytes = bytes.fromhex(account_hash_hex)
    tx_hash = contract.functions.flagAccount(
        account_hash_bytes,
        authority,
        EVIDENCE_BASIS_MAP[evidence_basis],
        risk_score,
        reason,
    ).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt.transactionHash.hex()


def is_blacklisted(account_hash_hex: str) -> bool:
    account_hash_bytes = bytes.fromhex(account_hash_hex)
    return contract.functions.isBlacklisted(account_hash_bytes).call()


def get_proof(account_hash_hex: str) -> dict:
    account_hash_bytes = bytes.fromhex(account_hash_hex)
    flagged_by, authority, evidence_basis, risk_score, reason, block_timestamp = (
        contract.functions.getProof(account_hash_bytes).call()
    )
    return {
        "flagged_by": flagged_by,
        "authority": authority,
        "evidence_basis": EVIDENCE_BASIS_REVERSE[evidence_basis],
        "risk_score": risk_score,
        "reason": reason,
        "block_timestamp": block_timestamp,
    }