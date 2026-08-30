"""
scripts/deploy_contract.py

Compiles and deploys MuleAccountRegistry.sol to a local Ganache
instance, then saves the ABI + deployed address so
app/web3_service.py can talk to it.

REQUIRES:
    pip install web3 py-solc-x
    Ganache running locally (default assumed: http://127.0.0.1:7545 —
    change GANACHE_URL if your Ganache UI/CLI uses a different port,
    e.g. 8545).

Run from backend/:
    python -m scripts.deploy_contract
"""

import json
from pathlib import Path

import solcx
from web3 import Web3

GANACHE_URL = "http://127.0.0.1:8545"  # confirmed from actual `ganache` CLI output
SOLC_VERSION = "0.8.19"
CONTRACT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "MuleAccountRegistry.sol"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "deployed_address.json"


def compile_contract():
    solcx.install_solc(SOLC_VERSION)
    source = CONTRACT_PATH.read_text()
    compiled = solcx.compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
    )
    _, contract_interface = compiled.popitem()
    return contract_interface["abi"], contract_interface["bin"]


def deploy():
    abi, bytecode = compile_contract()

    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    if not w3.is_connected():
        raise ConnectionError(
            f"Could not connect to Ganache at {GANACHE_URL} — is it running?"
        )

    w3.eth.default_account = w3.eth.accounts[0]
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = Contract.constructor().transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Deployed MuleAccountRegistry at: {tx_receipt.contractAddress}")

    OUTPUT_PATH.write_text(
        json.dumps({"address": tx_receipt.contractAddress, "abi": abi}, indent=2)
    )
    print(f"Saved ABI + address to {OUTPUT_PATH}")

    return tx_receipt.contractAddress, abi


if __name__ == "__main__":
    deploy()