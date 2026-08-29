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
* [x] Automated contract testing
* [x] Web3.py integration
* [x] FastAPI integration
* [x] Swagger API documentation
* [x] JavaScript compatibility scripts
* [x] Environment-based configuration
* [x] Automatic contract address management

# Problem Statement

Cybercriminals often route stolen funds through multiple intermediary ("mule") accounts before withdrawing cash through ATMs or bank branches.

Traditional databases allow records to be modified, deleted, or manipulated by privileged users.

CyberSight addresses this challenge by maintaining an immutable blockchain ledger of known mule accounts, ensuring:

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

* Immutable flagged account records
* Tamper-resistant audit trail
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
* Immutable blockchain audit trail
* Web3.py integration
* FastAPI integration
* Swagger API documentation
* Automated deployment workflow
* Automated testing workflow
* Persistent blockchain workspace

# Smart Contract

## MuleAccountRegistry.sol

The smart contract stores and manages mule account records.

## Stored Information

| Field     | Description                              |
| --------- | ---------------------------------------- |
| flagged   | Whether the account is currently flagged |
| riskScore | Mule account risk score                  |
| timestamp | Time the account was flagged             |
| reason    | Reason for flagging                      |

## Data Structure

```solidity
struct MuleAccount {
    bool flagged;
    uint256 riskScore;
    uint256 timestamp;
    string reason;
}
```

## Functions

### flagAccount()

Stores mule account evidence on-chain.

```solidity
flagAccount(
    accountId,
    riskScore,
    reason
)
```

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

Returns complete account information.

```solidity
getAccountDetails(accountId)
```

Returns:

```solidity
(
    bool flagged,
    uint256 riskScore,
    uint256 timestamp,
    string reason
)
```

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
    string accountId,
    uint256 riskScore,
    uint256 timestamp
);
```

Emitted whenever a mule account is flagged.

### AccountUnflagged

```solidity
event AccountUnflagged(
    string accountId,
    uint256 timestamp
);
```

Emitted whenever a mule account is unflagged.

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
├── .env
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

```json
{
  "account_id": "MULE123",
  "risk_score": 95,
  "reason": "Detected by CyberSight ML"
}
```

Response:

```json
{
  "success": true,
  "account_id": "MULE123",
  "tx_hash": "0x..."
}
```

## Check Account

GET /api/blockchain/check/MULE123

Response:

```json
{
  "blacklisted": true,
  "risk_score": 95,
  "flagged_at": 1782279729,
  "reason": "Detected by CyberSight ML"
}
```

# Installation

## Clone Repository

```bash
git clone https://github.com/kartike37/cybercrime-prediction-sih
cd blockchain
```

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
* `PRIVATE_KEY` comes from `.env` and is used for deployment.
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

# Development Deployment

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

* Private Ethereum network
* Immutable audit trail
* Environment variable isolation
* Smart contract transaction logging
* Blockchain-backed verification
* Future role-based authorization
* Transparent registry management

# Future Scope

* Consortium blockchain deployment
* Multi-bank blockchain integration
* Event indexing
* Backend integration
* Dashboard visualization
* Cross-agency intelligence sharing

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

This blockchain module was developed as part of the CyberSight project for Smart India Hackathon 2025 to provide a secure, immutable, and auditable mule account intelligence platform for cybercrime investigations.

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
