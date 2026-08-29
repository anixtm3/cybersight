import json
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from web3 import Web3


ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"


# -----------------------------------
# LOAD ENVIRONMENT
# -----------------------------------

load_dotenv(ENV_PATH)

GANACHE_RPC_URL = os.getenv("GANACHE_RPC_URL")

if not GANACHE_RPC_URL:
    raise Exception(
        "GANACHE_RPC_URL not found in .env"
    )


# -----------------------------------
# LOAD CONFIG
# -----------------------------------

with open(ROOT_DIR / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

CONTRACT_ADDRESS = Web3.to_checksum_address(
    config["contract"]["address"]
)

ABI_PATH = config["abi"]["path"]


# -----------------------------------
# CONNECT TO GANACHE
# -----------------------------------

w3 = Web3(
    Web3.HTTPProvider(GANACHE_RPC_URL)
)

if not w3.is_connected():
    raise Exception(
        "Failed to connect to Ganache"
    )


# -----------------------------------
# LOAD ABI
# -----------------------------------

with open(ABI_PATH, "r") as f:
    contract_json = json.load(f)

ABI = contract_json["abi"]


# -----------------------------------
# LOAD CONTRACT
# -----------------------------------

contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=ABI
)


# -----------------------------------
# DEFAULT ACCOUNT
# -----------------------------------

owner_account = w3.eth.accounts[0]


# -----------------------------------
# FLAG ACCOUNT
# -----------------------------------

def flag_mule_account(
    account_id,
    risk_score,
    reason
):

    tx_hash = contract.functions.flagAccount(
        account_id,
        risk_score,
        reason
    ).transact({
        "from": owner_account
    })

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    return receipt.transactionHash.hex()


# -----------------------------------
# CHECK BLACKLIST
# -----------------------------------

def check_blacklist(
    account_id
):

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
        "blacklisted": blacklisted,
        "risk_score": details[1],
        "flagged_at": details[2],
        "reason": details[3]
    }


# -----------------------------------
# TEST
# -----------------------------------

if __name__ == "__main__":

    tx = flag_mule_account(
        "CYBER123",
        90,
        "Detected by CyberSight ML"
    )

    print(
        "Transaction Hash:",
        tx
    )

    result = check_blacklist(
        "CYBER123"
    )

    print(result)
