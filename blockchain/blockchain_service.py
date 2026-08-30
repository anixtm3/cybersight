import json
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from web3 import Web3


ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"
CONFIG_PATH = ROOT_DIR / "config.yaml"


# -----------------------------------
# LOAD ENVIRONMENT
# -----------------------------------

load_dotenv(ENV_PATH)

GANACHE_RPC_URL = os.getenv("GANACHE_RPC_URL")

if not GANACHE_RPC_URL:
    raise ValueError(
        "GANACHE_RPC_URL not found in .env"
    )


# -----------------------------------
# LOAD CONFIG
# -----------------------------------

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

CONTRACT_ADDRESS = Web3.to_checksum_address(
    config["contract"]["address"]
)

ABI_PATH = ROOT_DIR / Path(
    config["abi"]["path"]
).as_posix().replace("./", "")


# -----------------------------------
# LOAD ABI
# -----------------------------------

with open(ABI_PATH, "r", encoding="utf-8") as f:
    contract_json = json.load(f)

ABI = contract_json["abi"]


# -----------------------------------
# WEB3 CONNECTION
# -----------------------------------

def get_web3():
    """
    Create a Web3 connection to Ganache.

    Returns:
        Web3 instance if connected.
        None if Ganache is unavailable.
    """

    try:
        w3 = Web3(
            Web3.HTTPProvider(
                GANACHE_RPC_URL,
                request_kwargs={"timeout": 5}
            )
        )

        if not w3.is_connected():
            return None

        return w3

    except Exception:
        return None


# -----------------------------------
# CONTRACT
# -----------------------------------

def get_contract(w3):
    return w3.eth.contract(
        address=CONTRACT_ADDRESS,
        abi=ABI
    )


# -----------------------------------
# FLAG ACCOUNT
# -----------------------------------

def flag_mule_account(
    account_id,
    risk_score,
    reason,
    flagging_authority,
    evidence_basis
):
    """
    Flag an account on-chain.

    The Solidity contract hashes account_id before
    storing it on-chain.

    Returns:
        {
            "success": True,
            "transaction_hash": "...",
            "block_number": ...
        }

    If Ganache is unavailable:
        {
            "success": False,
            "transaction_hash": None,
            "block_number": None
            "error": "Blockchain unavailable"
        }
    """

    w3 = get_web3()

    if w3 is None:
        return {
            "success": False,
            "transaction_hash": None,
            "block_number": None,
            "error": "Blockchain unavailable"
        }

    try:
        contract = get_contract(w3)

        owner_account = w3.eth.accounts[0]

        tx_hash = contract.functions.flagAccount(
            account_id,
            int(risk_score),
            reason,
            flagging_authority,
            evidence_basis
        ).transact({
            "from": owner_account
        })

        receipt = w3.eth.wait_for_transaction_receipt(
            tx_hash,
            timeout=10
        )

        return {
            "success": True,
            "transaction_hash": w3.to_hex(receipt.transactionHash),
            "block_number": receipt.blockNumber
        }

    except Exception as exc:
        return {
            "success": False,
            "transaction_hash": None,
            "block_number": None,
            "error": str(exc)
        }


# -----------------------------------
# CHECK BLACKLIST
# -----------------------------------

def check_blacklist(account_id):
    """
    Check whether an account is flagged and retrieve
    its on-chain provenance information.
    """

    w3 = get_web3()

    if w3 is None:
        return {
            "success": False,
            "blacklisted": False,
            "error": "Blockchain unavailable"
        }

    try:
        contract = get_contract(w3)

        blacklisted = (
            contract.functions
            .isBlacklisted(account_id)
            .call()
        )

        details = (
            contract.functions
            .getAccountDetails(account_id)
            .call()
        )

        return {
            "success": True,
            "blacklisted": blacklisted,
            "risk_score": details[1],
            "flagged_at": details[2],
            "reason": details[3],
            "flagging_authority": details[4],
            "evidence_basis": details[5],
            "account_hash": w3.to_hex(details[6])
        }

    except Exception as exc:
        return {
            "success": False,
            "blacklisted": False,
            "error": str(exc)
        }


# -----------------------------------
# TEST
# -----------------------------------

if __name__ == "__main__":

    print("Testing blockchain connection...")

    w3 = get_web3()

    if w3 is None:
        print("Ganache unavailable.")
        raise SystemExit(1)

    print(
        "Connected to Ganache:",
        GANACHE_RPC_URL
    )

    print(
        "Contract:",
        CONTRACT_ADDRESS
    )

    result = flag_mule_account(
        account_id="CYBER123",
        risk_score=90,
        reason="Detected by CyberSight ML",
        flagging_authority="CYBERSIGHT_ADMIN",
        evidence_basis="INVESTIGATION_VERIFIED"
    )

    print("\nFlag result:")
    print(result)

    if result["success"]:

        result = check_blacklist(
            "CYBER123"
        )

        print("\nRead-back result:")
        print(result)
