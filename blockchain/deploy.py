import json
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from web3 import Web3


ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"
CONFIG_PATH = ROOT_DIR / "config.yaml"
ARTIFACT_PATH = (
    ROOT_DIR
    / "artifacts"
    / "contracts"
    / "MuleAccountRegistry.sol"
    / "MuleAccountRegistry.json"
)
ARTIFACT_RELATIVE_PATH = Path(
    "artifacts/contracts/MuleAccountRegistry.sol/"
    "MuleAccountRegistry.json"
)
CONFIG_ABI_PATH = f"./{ARTIFACT_RELATIVE_PATH.as_posix()}"


def load_environment():
    load_dotenv(ENV_PATH)

    rpc_url = os.getenv("GANACHE_RPC_URL")
    private_key = os.getenv("PRIVATE_KEY")

    if not rpc_url:
        raise ValueError(
            "GANACHE_RPC_URL not found in .env"
        )

    if not private_key:
        raise ValueError(
            "PRIVATE_KEY not found in .env"
        )

    return rpc_url, private_key


def load_artifact():
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as artifact_file:
        artifact = json.load(artifact_file)

    abi = artifact.get("abi")
    bytecode = artifact.get("bytecode")

    if not abi or not bytecode:
        raise ValueError(
            "ABI or bytecode missing from compiled artifact"
        )

    return abi, bytecode


def update_config(contract_address, rpc_url):
    config = {}

    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}

    config["contract"] = {
        "address": Web3.to_checksum_address(contract_address)
    }
    config["ganache"] = {
        "rpc_url": rpc_url
    }
    config["abi"] = {
        "path": CONFIG_ABI_PATH
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as config_file:
        yaml.safe_dump(
            config,
            config_file,
            sort_keys=False
        )


def main():
    rpc_url, private_key = load_environment()
    abi, bytecode = load_artifact()

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        raise ConnectionError(
            f"Failed to connect to Ganache at {rpc_url}"
        )

    account = w3.eth.account.from_key(private_key)
    contract = w3.eth.contract(
        abi=abi,
        bytecode=bytecode
    )

    nonce = w3.eth.get_transaction_count(account.address)
    gas_estimate = contract.constructor().estimate_gas({
        "from": account.address
    })

    deployment_tx = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
        "gas": int(gas_estimate * 1.2),
        "gasPrice": w3.eth.gas_price
    })

    signed_tx = w3.eth.account.sign_transaction(
        deployment_tx,
        private_key=private_key
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed_tx.raw_transaction
    )

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    contract_address = receipt.contractAddress

    if not contract_address:
        raise RuntimeError(
            "Deployment completed without a contract address"
        )

    update_config(contract_address, rpc_url)

    print(
        "Contract Address:",
        Web3.to_checksum_address(contract_address)
    )
    print(
        "Transaction Hash:",
        w3.to_hex(receipt.transactionHash)
    )
    print(
        "Block Number:",
        receipt.blockNumber
    )


if __name__ == "__main__":
    main()
