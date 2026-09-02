# CyberSight Blockchain Module

> Ethereum-based Mule Account Registry for CyberSight (Smart India Hackathon 2025 – PS 77)

# Overview

The Blockchain Module is a core component of **CyberSight**, a predictive analytics framework developed for **Smart India Hackathon 2025 (PS 77)** under the **Ministry of Home Affairs (MHA)** and the **Indian Cybercrime Coordination Centre (I4C)**.

This module maintains a tamper-resistant registry of identified mule bank accounts using a private Ethereum blockchain built with **Ganache**, **Solidity**, **Hardhat** for compilation, and **Web3.py** for deployment and runtime access.

By storing verified mule account records on-chain, CyberSight enables trusted inter-agency intelligence sharing while ensuring transparency, integrity, and auditability.

```text
Hardhat
        |
        ▼
Compile Solidity
        |
        ▼
Artifacts
        |
        ▼
deploy.py (Web3.py)
        |
        ▼
config.yaml
        |
        ▼
blockchain_service.py
        |       
        ▼
blockchain_api.py
        |
        ▼
CyberSight Backend
```

# Development Status

## Blockchain Sprint 2: Complete

### Implemented Features

* [x] Ganache local blockchain setup
* [x] Hardhat development environment
* [x] MuleAccountRegistry smart contract
* [x] Owner-only administrative controls
* [x] Account flagging system
* [x] Account unflagging system
* [x] Flagged account verification system
* [x] Account detail retrieval
* [x] AccountFlagged event
* [x] AccountUnflagged event
* [x] Automated contract deployment
* [x] End-to-end blockchain testing
* [x] Web3.py integration
* [x] FastAPI integration
* [x] Swagger API documentation
* [x] JavaScript compatibility scripts
* [x] Environment-based configuration
* [x] Automatic contract address management

# Problem Statement

Cybercriminals often route stolen funds through multiple intermediary ("mule") accounts before withdrawing cash through ATMs or bank branches.

Traditional databases allow records to be modified, deleted, or manipulated by privileged users.

CyberSight addresses this challenge by maintaining a blockchain ledger of known mule accounts with auditable transaction history, ensuring:

* Tamper-resistant record storage
* Verifiable audit trail
* Shared intelligence across agencies
* Increased trust in mule account registry data
* Transparent investigation history

# System Architecture

```text
CyberSight Backend
        │
        ▼
blockchain_api.py
        │
        ▼
blockchain_service.py
        │
        ▼
config.yaml
        │
        ▼
Web3.py
        │
        ▼
MuleAccountRegistry.sol
        │
        ▼
Ganache
```

# Technology Stack

| Component              | Technology               |
| ---------------------- | ------------------------ |
| Blockchain Network     | Ethereum private network |
| Local Blockchain       | Ganache                  |
| Smart Contracts        | Solidity                 |
| Contract Compilation   | Hardhat                  |
| Deployment and Runtime | Web3.py                  |
| Backend API            | FastAPI                  |
| Environment Variables  | python-dotenv            |
| Configuration Format   | YAML                     |
| Runtime Environment    | Node.js + Python         |

# Why Blockchain?

CyberSight uses blockchain technology to ensure that mule account intelligence cannot be silently altered, removed, or manipulated.

### Benefits

* Tamper-resistant on-chain registry with auditable transaction history
* Historical blockchain transactions that cannot be erased
* Trustworthy inter-agency intelligence sharing
* Transparent investigation history
* Reduced insider manipulation risk
* Verifiable transaction logging

This directly supports cybercrime investigation workflows where data integrity is critical.

# Features

## Current Features

* Flag mule accounts on-chain
* Unflag false-positive mule accounts
* Check flagged account status
* Retrieve complete account details
* Owner-only administrative controls
* Tamper-resistant on-chain registry with an auditable transaction history
* Web3.py integration
* FastAPI integration
* Swagger API documentation
* Automated deployment workflow
* Automated testing workflow
* Persistent blockchain workspace

# Smart Contract

## MuleAccountRegistry.sol

The smart contract stores and manages mule account records.

## Storage Design

Account identifiers are **hashed using keccak256** before being used as registry storage keys. The plaintext identifier is not stored in the contract's persistent registry state.

Note: The plaintext account identifier does appear in transaction calldata, which is visible on the blockchain. Hashing the identifier in the contract prevents it from being used as the mapping key.

```solidity
mapping(bytes32 => MuleAccount) private muleAccounts;
```

## Stored Information

| Field               | Type                | Description                                 |
| ------------------- | ------------------- | --------------------------------------------|
| flagged             | `bool`              | Whether the account is currently flagged    |
| riskScore           | `uint256`           | Mule account risk score                     |
| timestamp           | `uint256`           | Unix timestamp when the account was flagged |
| reason              | `string`            | Reason for flagging                         |
| flaggingAuthority   | `string`            | Authority that flagged the account          |
| evidenceBasis       | `string`            | Classification of evidence (see below)      |

## Data Structure

```solidity
struct MuleAccount {
    bool flagged;
    uint256 riskScore;
    uint256 timestamp;
    string reason;
    string flaggingAuthority;
    string evidenceBasis;
}
```

## Functions

### flagAccount()

Stores mule account evidence on-chain with provenance information.

```solidity
flagAccount(
    string memory accountId,
    uint256 riskScore,
    string memory reason,
    string memory flaggingAuthority,
    string memory evidenceBasis
)
```

**Parameters:**

- `accountId`: The plaintext account identifier (hashed internally)
- `riskScore`: Numeric risk score (0-100+)
- `reason`: Description of why the account was flagged
- `flaggingAuthority`: Organization or authority that flagged the account
- `evidenceBasis`: Classification of evidence (see below)

**Evidence Basis Values:**

Only the following exact values are accepted:

- `INVESTIGATION_VERIFIED` – Account flagged based on verified investigation
- `MONITORING_SUSPECTED` – Account flagged based on monitoring and suspicion

Unsupported evidence basis values are rejected by the contract.

**Access Control:**

Only the contract owner can call this function.

### isBlacklisted()

Checks whether an account is currently flagged.

```solidity
isBlacklisted(accountId)
```

Returns:

```solidity
true / false
```

### getAccountDetails()

Returns complete account information and on-chain provenance.

```solidity
getAccountDetails(string memory accountId)
```

Returns:

```solidity
(
    bool flagged,
    uint256 riskScore,
    uint256 timestamp,
    string memory reason,
    string memory flaggingAuthority,
    string memory evidenceBasis,
    bytes32 accountHash
)
```

**Return Values:**

- `flagged`: Current flagged status
- `riskScore`: Stored risk score
- `timestamp`: Unix timestamp when flagged
- `reason`: Reason for flagging
- `flaggingAuthority`: Organization that flagged the account
- `evidenceBasis`: Classification of evidence
- `accountHash`: The keccak256 hash of the account identifier

### unflagAccount()

Removes flagged status for false-positive handling.

```solidity
unflagAccount(accountId)
```

Only the contract owner can call this function.

# Blockchain Audit Events

### AccountFlagged

```solidity
event AccountFlagged(
    bytes32 indexed accountHash,
    uint256 riskScore,
    uint256 timestamp,
    string flaggingAuthority,
    string evidenceBasis
);
```

Emitted whenever a mule account is flagged.

**Note:** The event uses the `accountHash` (keccak256 hash), not the plaintext account identifier.

### AccountUnflagged

```solidity
event AccountUnflagged(
    bytes32 indexed accountHash,
    uint256 timestamp
);
```

Emitted whenever a mule account is unflagged.

**Note:** The event uses the `accountHash` (keccak256 hash), not the plaintext account identifier.

These events provide a permanent and immutable blockchain audit trail.

# Project Structure

```text
blockchain/
│
├── artifacts/
├── contracts/
│   └── MuleAccountRegistry.sol
│
├── ignition/
│   └── modules/
│       └── Lock.js
│
├── scripts/
│   ├── deploy.js            # deprecated legacy deployment helper
│   └── testContract.js
│
├── blockchain_service.py
├── blockchain_api.py
├── deploy.py
├── config.yaml
├── requirements.txt
│
├── .gitignore
├── hardhat.config.js
├── package.json
├── package-lock.json
└── README.md
```

## Important Files

### contracts/MuleAccountRegistry.sol

Contains the smart contract responsible for managing mule account records.

### deploy.py

Primary deployment script.

Responsibilities:

* Load `.env` using `python-dotenv`
* Read the compiled contract artifact from `artifacts/`
* Deploy the contract using Web3.py
* Retrieve the deployed contract address
* Automatically update `config.yaml`
* Simplify redeployment workflow

### scripts/testContract.js

Responsibilities:

* Read the contract address from `config.yaml`
* Connect to the deployed contract
* Execute basic functional checks
* Verify blockchain connectivity

### scripts/deploy.js

Deprecated legacy deployment helper retained for backward compatibility. Deployment is currently handled by `deploy.py`.

# Python Blockchain Integration

## blockchain_service.py

Provides Python access to the blockchain using Web3.py.

### Functions

#### flag_mule_account()

Stores mule account evidence on-chain.

#### check_blacklist()

Retrieves the current registry state for a given account.

## config.yaml

Stores:

- The deployed contract address
- The ABI path

`config.yaml` is the source of truth for the deployed contract address and ABI path. The deployment script writes these values automatically.

# FastAPI Integration

## blockchain_api.py

Provides REST endpoints for CyberSight backend integration.

### POST /api/blockchain/flag

Stores mule account evidence on-chain.

### GET /api/blockchain/check/{account_id}

Retrieves the current flagged state and account details for a specific account.

### Swagger Documentation

Available at:

```text
http://127.0.0.1:8000/docs
```

# API Examples

## Flag Account

POST /api/blockchain/flag

**Request:**

```json
{
  "account_id": "MULE123",
  "risk_score": 95,
  "reason": "Detected by CyberSight ML",
  "flagging_authority": "CyberSight ML",
  "evidence_basis": "INVESTIGATION_VERIFIED"
}
```

**Response (Success):**

```json
{
  "success": true,
  "account_id": "MULE123",
  "tx_hash": "0x...",
  "block_number": 123,
  "error": null
}
```

**Response (Blockchain Unavailable):**

```json
{
  "success": false,
  "account_id": "MULE123",
  "tx_hash": null,
  "block_number": null,
  "error": "Blockchain unavailable"
}
```

## Check Account

GET /api/blockchain/check/MULE123

**Response (Account Found and Flagged):**

```json
{
  "success": true,
  "blacklisted": true,
  "risk_score": 95,
  "flagged_at": 1234567890,
  "reason": "Detected by CyberSight ML",
  "flagging_authority": "CyberSight ML",
  "evidence_basis": "INVESTIGATION_VERIFIED",
  "account_hash": "0x...",
  "error": null
}
```

**Response (Account Not Found):**

```json
{
  "success": true,
  "blacklisted": false,
  "risk_score": null,
  "flagged_at": null,
  "reason": null,
  "flagging_authority": null,
  "evidence_basis": null,
  "account_hash": null,
  "error": null
}
```

**Response (Blockchain Unavailable):**

```json
{
  "success": false,
  "blacklisted": false,
  "risk_score": null,
  "flagged_at": null,
  "reason": null,
  "flagging_authority": null,
  "evidence_basis": null,
  "account_hash": null,
  "error": "Blockchain unavailable"
}
```

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd blockchain
```

> Replace `<repository-url>` with the actual repository URL.

## Install Node.js Dependencies

```bash
npm install
```

## Create Python Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

### Windows (PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```

### Windows (CMD)

```cmd
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:

- Web3.py
- FastAPI
- Uvicorn
- PyYAML
- python-dotenv

# Ganache Setup

1. Install Ganache
2. Launch Ganache
3. Create a Persistent Workspace
4. Configure the workspace
5. Note:
   * RPC URL
   * Account Address
   * Private Key

Example:

```text
RPC URL:
http://127.0.0.1:7545
```

## Why Use a Persistent Workspace?

CyberSight uses a saved Ganache workspace instead of creating a new Quickstart blockchain each session.

Benefits:

* Preserves wallet accounts
* Preserves private keys
* Preserves transaction history
* Preserves blockchain state
* Simplifies development workflow

# Environment Configuration

Create a `.env` file:

```env
GANACHE_RPC_URL=http://127.0.0.1:7545
PRIVATE_KEY=YOUR_PRIVATE_KEY
```

### Notes

* `GANACHE_RPC_URL` comes from `.env` and points to the Ganache blockchain.
* `PRIVATE_KEY` is used by `deploy.py` to sign contract deployment transactions. Runtime flagging currently uses Ganache's first unlocked account.
* The contract address is stored in `config.yaml`.
* The ABI path is stored in `config.yaml`.
* `deploy.py` updates `config.yaml` automatically after deployment.

> Never commit `.env` to version control.

# Compile Contract

```bash
npx hardhat compile
```

Hardhat is used to compile the Solidity artifact consumed by `deploy.py`.

Expected Output:

```text
Compiled 1 Solidity file successfully
```

# Deploy Contract

```bash
python deploy.py
```

Responsibilities:

* Read `GANACHE_RPC_URL` and `PRIVATE_KEY` from `.env`
* Load the compiled contract artifact from `artifacts/`
* Deploy the contract using Web3.py
* Write the deployed contract address and ABI path to `config.yaml`

`config.yaml` stores the deployed contract address used by the Python blockchain layer.

Example Output:

```text
Contract Address: 0x338Fe18BD95783BA1ba05d844B1c5B2D2C436F24
Transaction Hash: 0x...
Block Number: 123
```

# Run API

Start the FastAPI server:

```bash
uvicorn blockchain_api:app --reload
```

Expected Output:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

# Current Deployment

**Network:** Ganache (Private Ethereum)

**RPC URL:** http://127.0.0.1:7545

**Contract Address:** 0x909457ddC90cd429C140027ea776d070cD99137a

**Deployment Transaction:** 0x43174d470421abac8076258aae5582b516adadf35936faae1286c68e56bbf8de

**Deployment Block:** 11

Each deployment updates `config.yaml` automatically, refreshing the deployed contract address and ABI path so the Python runtime always uses the latest deployed contract.

```text
Network:
Ganache Local Blockchain
```

# CyberSight Integration Workflow

```text
Complaint Received
        │
        ▼
ML Model Flags Mule Account
        │
        ▼
POST /api/blockchain/flag
        │
        ▼
blockchain_api.py
        │
        ▼
blockchain_service.py
        │
        ▼
MuleAccountRegistry
        │
        ▼
Blockchain Evidence Stored
        │
        ▼
Transaction Hash Returned
```

## Query Workflow

```text
Complaint Received
        │
        ▼
CyberSight Backend
        │
        ▼
blockchain_api.py
        │
        ▼
blockchain_service.py
        │
        ▼
MuleAccountRegistry.sol
        │
        ▼
Blockchain Response
        │
        ▼
Risk Intelligence Returned
```

# Security Considerations

* **Hashed Account Storage**: Account identifiers are hashed using keccak256 before being used as registry keys. The hash is not intended to provide complete anonymity; identifiers with a predictable format may still be susceptible to brute-force or dictionary attacks.
* **Owner-Only Operations**: `flagAccount()` and `unflagAccount()` are restricted to the contract owner via the `onlyOwner` modifier.
* **Evidence Basis Validation**: The contract strictly validates evidence basis values and rejects unsupported classifications.
* **Private Ethereum Network**: The contract runs on a private Ganache instance, not the public Ethereum network.
* **Immutable Audit Trail**: All flagging and unflagging events are permanently recorded on the blockchain.
* **Environment Variable Isolation**: Private keys and RPC URLs are loaded from `.env` and never committed to version control.
* **Transaction Hashes**: All operations return transaction hashes for verification and traceability.
* **Graceful Blockchain Failure**: The blockchain service returns structured failure responses when Ganache is unavailable, with a 5-second timeout to prevent hanging.
* **Transparent Registry Management**: Current account details are queryable through the contract, while historical registry actions can be audited through blockchain transactions and events.

# Blockchain Resilience

When Ganache is unavailable or unresponsive, the blockchain service returns graceful failure responses instead of hanging:

* HTTP timeout: 5 seconds
* Blockchain unavailable: Returns structured failure response with `success: false` and `error: "Blockchain unavailable"`
* API remains responsive and does not block

This allows CyberSight to continue operating even when blockchain connectivity is temporarily lost, with the ability to retry operations later.

# Validation & Testing

The current blockchain implementation has been verified to work correctly:

✅ Contract compilation succeeded with Hardhat

✅ Contract deployment succeeded on Ganache

✅ Account flagging succeeded with transaction hash returned

✅ Account read-back succeeded

✅ Evidence basis `INVESTIGATION_VERIFIED` successfully stored and read back

✅ Evidence basis `MONITORING_SUSPECTED` successfully stored and read back

✅ Account records remained readable after restarting Ganache using persistent workspace

✅ Graceful failure: When Ganache was stopped, the API returned structured failure (`success: false`, `error: "Blockchain unavailable"`) and remained responsive

✅ Swagger endpoint testing completed successfully at http://127.0.0.1:8000/docs

# Future Scope

* Consortium blockchain deployment (multi-bank participation)
* Stronger production authorization mechanisms
* Production-grade key management (HSM integration, key rotation)
* Event indexing for off-chain analytics
* CyberSight backend integration for automated flagging
* Dashboard visualization of on-chain proofs
* Cross-agency intelligence sharing protocols

# Team

## CyberSight – Smart India Hackathon 2025

| Name           | Role                           |
| -------------- | ------------------------------ |
| Rishika Garg   | ML / Data Engineer             |
| Himanshu Jain  | Full Stack Developer           |
| Aniket Dixit   | Blockchain Developer           |
| Kartike Rohila | Backend Developer              |
| Saina Sharma   | Database Engineer              |
| Kanav Agarwal  | Security & Compliance Engineer |

## Contribution

This blockchain module was developed as part of the CyberSight project for Smart India Hackathon 2025 to provide a secure, tamper-resistant, and auditable mule account intelligence platform for cybercrime investigations.

# Status

**Blockchain Sprint 2: Complete**

### Completed Deliverables

- MuleAccountRegistry smart contract
- Account flagging
- Account unflagging
- Flagged account verification
- Account detail retrieval
- AccountFlagged event
- AccountUnflagged event
- Automated deployment
- Automated testing
- Web3.py integration
- FastAPI integration
- Swagger API documentation
- End-to-end blockchain testing

### Next Phase

- CyberSight backend integration
- Automatic ML-to-blockchain flagging
- PostgreSQL transaction storage
- Dashboard blockchain indicators
