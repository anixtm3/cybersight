# CyberSight AI — Full Project

**Team INNOVAULT | ABESIT Ghaziabad | SIH 2026 | Problem Statement 26184 | MHA/I4C**

**Detect. Analyze. Verify. Protect.**

> *Before the ATM. Before the loss.*

CyberSight is a predictive analytics framework that detects, analyzes, and verifies mule account fraud networks in real-time. Developed for the Smart India Hackathon 2026 (Problem Statement PS 26184) under the **Ministry of Home Affairs (MHA)** and the **Indian Cybercrime Coordination Centre (I4C)**, CyberSight combines machine learning, blockchain-based registry, and investigator-centric intelligence dashboards to combat the mule account fraud ecosystem.

---

## Problem Statement 26184

**Ministry:** Ministry of Home Affairs (MHA) / Indian Cybercrime Coordination Centre (I4C)  
**Theme:** Blockchain & Cybersecurity  
**Portal:** Smart India Hackathon 2026

### The Problem
Cybercrime complaints in India are filed on the National Cybercrime Reporting Portal (NCRP). The typical fraud flow is:

1. Victim files complaint on NCRP after being defrauded
2. Complaint sits in queue for processing
3. Meanwhile, mule accounts have already withdrawn cash from ATMs
4. By the time LEA acts, the money is gone

**There is no existing system that predicts WHERE the cash will be withdrawn BEFORE it happens.**

### Existing Gaps Addressed
1. No predictive ATM-level risk scoring from complaint data
2. No real-time simultaneous alert dispatch to LEA + Bank + I4C
3. No immutable cross-state audit trail for flagged mule accounts
4. No GIS visualization of complaint hotspots with ATM-level drill-down
5. No role-differentiated dashboards for Cyber Cell / I4C / Bank Nodal Officers
6. No explainability layer (why was this ATM predicted?)

### CyberSight's Solution

CyberSight AI is a predictive analytics platform that:

1. **Ingests** cybercrime complaints via a REST API endpoint
2. **Extracts** 19 ML features from complaint data + real-time DB queries
3. **Predicts** the most likely ATM cluster for cash withdrawal using XGBoost (90% Top-1 accuracy)
4. **Ranks** Top-5 ATMs within the predicted district using PostGIS nearest-neighbor query
5. **Dispatches** real-time alerts simultaneously to Cyber Cell, I4C, Bank Nodal Officer, and Police SHO via WebSocket and Webhook
6. **Visualizes** fraud risk on a GIS choropleth heatmap with ATM-level drill-down
7. **Records** flagged mule accounts on an immutable Ganache blockchain with keccak256 hashing
8. **Explains** every prediction via SHAP feature attribution (real TreeExplainer, not hardcoded)
9. **Enables** response actions: Deploy Team, Alert Bank/ATM, Mark Resolved, Download PDF Report

---

## Team INNOVAULT

| Member | Role | Primary Technology |
|--------|------|---------|
| **Saina** | Team Lead + Database Engineer + ML Engineer | PostgreSQL, PostGIS, XGBoost, SHAP, Python |
| **Kartike** | Backend Engineer | FastAPI, Python 3.11, SQLAlchemy, WebSocket |
| **Himanshu** | Frontend Engineer | React 18, TypeScript, TailwindCSS, Leaflet.js |
| **Kanav** | Security Engineer | JWT, RBAC, bcrypt, pytest |
| **Aniket** | Blockchain Engineer + GitHub Manager | Solidity, Web3.py, Ganache |
| **Rishika** | Original ML Engineer (departed mid-project) | XGBoost design, feature engineering design |

---

## Key Features

### Deployed Functionality

- ✅ **User Authentication & Authorization** — JWT-based access control with three roles (Cyber Cell Officer, Bank Nodal Officer, I4C Admin) and jurisdiction/bank scoping
- ✅ **Complaint Ingestion Pipeline** — Real-time validation, keyword-based fraud type detection, duplicate checking, 6-hour rolling risk aggregation
- ✅ **ML-Powered ATM Prediction** — XGBoost classifier trained on 419K+ synthetic complaints; returns ranked Top-5 ATMs per predicted withdrawal district
- ✅ **Real-Time Risk Assessment** — Automatic classification into LOW/MEDIUM/HIGH risk levels; MEDIUM+ triggers WebSocket broadcast and 4-channel alert dispatch (SMS/Email/Webhook/Dashboard)
- ✅ **WebSocket Live Alerts** — Bi-directional real-time alert feed with JWT authentication; officers see MEDIUM/HIGH events instantly across the platform
- ✅ **Blockchain Mule Registry** — Ganache-backed Solidity smart contract (MuleAccountRegistry) flags verified mule accounts with Keccak-256 hashing, risk scores, and audit trail; immutable on-chain record
- ✅ **GIS Risk Heatmaps** — PostGIS-powered district-level risk choropleth; drill-down to ranked ATM lists; real 4,625 ATMs from Overpass Turbo (10 districts across India)
- ✅ **Role-Based Dashboards** — Cyber Cell (investigation-focused, district-scoped), Bank Nodal (freeze/action-focused), I4C Admin (cross-jurisdictional oversight)
- ✅ **SHAP Explainability** — Per-prediction SHAP values logged and visualized; shows directional influence of location, amount, network factors
- ✅ **Model Explainability Panel** — Interactive SHAP chart in frontend; displays top features driving each prediction
- ✅ **Audit & Evidence Trail** — Case notes, action logs, dispatch logs, and blockchain provenances for complete investigation history
- ✅ **Reports & Export** — District-wise, bank-wise, and fraud-typology-wise aggregates; CSV export support
- ✅ **Rate Limiting** — 5-attempt threshold on failed login attempts; SlowAPI enforces per-IP limits
- ✅ **Account Identifier Protection** — Account IDs hashed server-side via Keccak-256 before blockchain storage; plaintext never on-chain

---

## System Architecture

CyberSight is a five-tier system:

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React 18 + TypeScript)                       │
│  • Login, Role-based Dashboards                         │
│  • Command Centre (live WebSocket feed)                 │
│  • GIS Heatmap (Leaflet), SHAP Charts (Recharts)        │
│  • Mule Registry, Reports, Dispatch Logs                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP(S) + WebSocket
                     │ (JWT-authenticated)
┌────────────────────▼────────────────────────────────────┐
│  Backend API (FastAPI, Python 3.11)                     │
│  • /api/auth/login (JWT issuance)                       │
│  • /api/complaints/ingest (full pipeline)               │
│  • /api/predict (ML inference)                          │
│  • /api/heatmap (GIS queries)                           │
│  • /api/mule/* (registry operations)                    │
│  • /api/complaints/{id}/notes, actions (evidence)       │
│  • /ws/alerts (real-time broadcast)                     │
│  • Rate Limiting: SlowAPI, per-IP limits                │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼──────────┐
         │           │          │
┌────────▼──────┐ ┌──▼────────┐ │
│  PostgreSQL + │ │ XGBoost   │ │
│  PostGIS      │ │ ML Model  │ │
│  • Complaints │ │ • 19 feat │ │
│  • Users      │ │ • 90% top │ │
│  • ATMs       │ │   -1 accy │ │
│  • Predictions│ │ • SHAP    │ │
│  • Mule Acc   │ │   explnbl │ │
│  • Evidence   │ │           │ │
│  4,625 ATMs   │ │           │ │
│  419K+ rows   │ │           │ │
└───────────────┘ └───────────┘ │
                                │
                    ┌───────────▼────────┐
                    │  Ganache Blockchain│
                    │  • MuleAccountReg. │
                    │  • Solidity        │
                    │  • Keccak-256      │
                    │  • Immutable Log   │
                    └────────────────────┘
```

### Component Interaction Flow

```
Complaint Ingest (POST /api/complaints/ingest)
    │
    ├─► Input Validation (null bytes, length checks)
    │
    ├─► Keyword-Based Fraud Type Detection
    │
    ├─► Duplicate Complaint ID Check
    │
    ├─► Save to Database
    │
    ├─► Compute 6 Real-Time Features (rolling count, district risk, ATM density, etc.)
    │
    ├─► Call XGBoost Model (ML)
    │       │
    │       └─► Predict withdrawal district
    │           └─► Rank Top-5 ATMs from predicted district
    │           └─► Compute SHAP values
    │           └─► Return if confidence >= 0.4
    │               (else: ANALYST_REVIEW, no auto-dispatch)
    │
    ├─► Save Prediction + SHAP to DB
    │
    ├─► Classify Risk Level (LOW/MEDIUM/HIGH)
    │
    ├─► If MEDIUM/HIGH:
    │   ├─► Broadcast WebSocket alert
    │   ├─► Write dispatch log (SMS/Email/Webhook/Dashboard channels)
    │   └─► If HIGH: Flag on blockchain (non-blocking, timeout-bounded)
    │
    └─► Return 200 OK + prediction details to client
```

---

## End-to-End Workflow

### User Journey: Fraud Detection to Blockchain Verification

**1. Complaint Receipt**
- Bank nodal officer or cyber cell officer submits a complaint via `/api/complaints/ingest`.
- Complaint includes victim details (location, account, amount), beneficiary account info, and narrative description.

**2. Real-Time Feature Computation**
- Backend queries database for:
  - 6-hour rolling complaint count in victim's district
  - Average district risk score
  - ATM density within 5km of victim location (PostGIS)
  - Time since last complaint from same beneficiary bank
  - Mule network flag (1 if number of hops ≥ 4)
  - Festival period flag (hardcoded to 0 for 2026)

**3. ML Inference**
- 19 features (exact order) passed to XGBoost model.
- Model predicts withdrawal district (10-class classification).
- SHAP TreeExplainer computes feature importance for that prediction.
- If confidence < 0.4 → status = `ANALYST_REVIEW` (no auto-dispatch).
- If confidence ≥ 0.4 → retrieve Top-5 ATMs from predicted district.

**4. Risk Stratification**
- Based on prediction confidence, amount, and district risk score, complaint assigned:
  - `LOW` — confidence < 0.4 or low-risk factors
  - `MEDIUM` — confidence 0.4–0.7
  - `HIGH` — confidence ≥ 0.7 + high-risk factors

**5. Real-Time Alert Dispatch**
- If MEDIUM:
  - WebSocket broadcast to connected investigators
  - Dispatch log written (Email/SMS/Webhook/Dashboard channels tracked)
- If HIGH:
  - WebSocket broadcast
  - Dispatch log written
  - **Non-blocking POST to blockchain API** (Ganache flag endpoint) to mark beneficiary as mule

**6. Blockchain Recording** (Async, Non-Blocking)
- Backend service calls blockchain API with beneficiary account ID and risk metadata.
- Blockchain hashes account ID (Keccak-256) and stores on-chain:
  - `accountHash` (bytes32, indexed)
  - `riskScore` (uint256)
  - `timestamp` (block.timestamp)
  - `reason`, `flaggingAuthority`, `evidenceBasis` (strings)
- Event emitted: `AccountFlagged` logged to blockchain event stream.
- If Ganache unavailable → ingest still returns 200 (graceful degrade).

**7. Investigation & Evidence Gathering**
- Cyber cell officer can:
  - View complaint + prediction + Top-5 ATM list
  - Add case notes via `POST /api/complaints/{id}/notes`
  - Log actions via `POST /api/complaints/{id}/actions`
  - View heatmap of complaints + predicted withdrawal zones
  - Drill down to specific ATMs and see risk scores

**8. Risk Heatmap & Analytics**
- I4C Admin and Cyber Cell officers visualize:
  - District-level risk choropleth (LOW/MEDIUM/HIGH) on Leaflet map
  - Filterable by date range, district, fraud type, risk level
  - ATM drill-down showing top 5 predicted withdrawal locations

**9. Mule Registry & Blockchain Proof**
- Cyber Cell Officer / I4C Admin views `/api/mule/registry` → table of flagged accounts
- For each flagged account:
  - Account identifier (obfuscated, never plaintext)
  - Risk score
  - Flagging authority (e.g., "Delhi Cyber Cell")
  - Evidence basis ("INVESTIGATION_VERIFIED" or "MONITORING_SUSPECTED")
  - Blockchain transaction hash
  - Block timestamp (immutable proof)
- Can query blockchain to verify integrity of flagging record.

**10. Cross-Agency Sharing**
- I4C Admin exports reports (CSV) for distribution to other agencies.
- All blockchain records are tamper-evident (Ganache ledger).
- Audit log records all sensitive actions (who, when, what) for compliance.

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React | 18.3.1 | UI framework |
| | TypeScript | 5.5.3 | Type safety |
| | Vite | 5.4.2 | Build tool / dev server |
| | React Router | 6.30.6 | Routing |
| | TailwindCSS | 3.4.1 | Styling |
| | Leaflet | 1.9.4 | GIS mapping |
| | Recharts | 2.15.4 | Charts (SHAP, reports) |
| | Lucide React | 0.446.0 | Icons |
| | Socket.IO Client | 4.8.3 | WebSocket real-time |
| **Backend** | FastAPI | Latest | API framework |
| | Python | 3.11 | Runtime |
| | Uvicorn | Latest | ASGI server |
| | SQLAlchemy | Latest | ORM |
| | Python-Jose | Latest | JWT encoding/decoding |
| | Passlib + Bcrypt | 4.0.1 | Password hashing |
| | Slowapi | Latest | Rate limiting |
| **Database** | PostgreSQL | 15 | Relational data |
| | PostGIS | 3.6.2 | Spatial queries |
| | Port | 5433 | Custom port |
| **ML** | XGBoost | Latest | Classification model |
| | SHAP | Latest | Model explainability |
| | Scikit-learn | Latest | Encoders, preprocessing |
| | Pandas | Latest | Data manipulation |
| | NumPy | Latest | Numerical computation |
| | GeoPandas | Latest | Spatial data |
| **Blockchain** | Ganache | 7.x | Local Ethereum testnet |
| | Solidity | 0.8.20 | Smart contracts |
| | Hardhat | 2.22.19 | Compilation, deployment |
| | Web3.py | Latest | Blockchain interaction |
| | Web3.js | Latest | JS contract testing |
| **DevOps** | Git | Latest | Version control |
| | Docker | (optional) | Containerization |

---

## Project Structure

```
cybersight/
├── README.md                          # Root README (this file)
├── LICENSE                            # Apache 2.0
│
├── frontend/                          # React SPA
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.tsx                   # Entry point
│   │   ├── App.tsx                    # Router + AuthProvider + SocketProvider
│   │   ├── index.css                  # TailwindCSS
│   │   ├── config.ts                  # API base URL, endpoints
│   │   ├── pages/
│   │   │   ├── Login.tsx              # Authentication
│   │   │   ├── DashboardPage.tsx      # Main dashboard
│   │   │   ├── HeatmapPage.tsx        # GIS risk heatmap
│   │   │   ├── AlertsPage.tsx         # WebSocket alert feed
│   │   │   ├── AlertDetailPage.tsx    # Single alert drill-down
│   │   │   ├── CyberCellDashboard.tsx # Cyber Cell Officer view
│   │   │   ├── BankNodalDashboard.tsx # Bank Nodal Officer view
│   │   │   ├── I4CAdminDashboard.tsx  # I4C Admin oversight view
│   │   │   ├── MuleRegistryPage.tsx   # Flagged accounts + blockchain proof
│   │   │   ├── BlockchainLogPage.tsx  # On-chain events
│   │   │   ├── ReportsPage.tsx        # Analytics + CSV export
│   │   │   ├── DispatchLogPage.tsx    # 4-channel delivery status
│   │   │   ├── SettingsPage.tsx       # User preferences
│   │   ├── components/
│   │   │   ├── ProtectedRoute.tsx     # JWT + role check
│   │   │   ├── RoleDashboard.tsx      # Role router
│   │   │   └── ... (UI components)
│   │   ├── context/
│   │   │   ├── AuthContext.tsx        # JWT token state
│   │   │   └── SocketContext.tsx      # WebSocket connection
│   │   ├── services/
│   │   │   └── api.ts                 # Axios client
│   │   ├── hooks/
│   │   │   └── ... (custom hooks)
│   │   └── mockData.ts                # Fallback mock data
│   └── public/
│
├── backend/                           # FastAPI service
│   ├── requirements.txt
│   ├── .env                           # DATABASE_URL, SECRET_KEY, etc.
│   ├── app/
│   │   ├── main.py                    # FastAPI app, middleware, CORS
│   │   ├── database.py                # SQLAlchemy engine, SessionLocal
│   │   ├── auth_core.py               # JWT, RBAC, jurisdiction scoping
│   │   ├── crypto_utils.py            # Encryption utilities
│   │   ├── utils.py                   # Helpers (tracking number, etc.)
│   │   ├── rate_limit.py              # SlowAPI rate limiter
│   │   ├── web3_service.py            # Web3.py blockchain integration
│   │   ├── models/
│   │   │   ├── complaint.py           # SQLAlchemy ORM models
│   │   │   │   └── User, Complaint, Prediction, MuleAccount, etc.
│   │   │   └── predict.py             # XGBoost inference, model loading
│   │   ├── schemas/
│   │   │   ├── complaint.py           # Pydantic request/response models
│   │   │   └── ...
│   │   └── routers/
│   │       ├── auth.py                # POST /api/auth/login
│   │       ├── ingest.py              # POST /api/complaints/ingest
│   │       ├── predict.py             # POST /api/predict
│   │       ├── heatmap.py             # GET /api/heatmap
│   │       ├── mule.py                # /api/mule/* (registry)
│   │       ├── evidence.py            # /api/complaints/{id}/notes, actions
│   │       ├── complaints.py          # GET /api/complaints
│   │       ├── reports.py             # GET /api/reports
│   │       ├── websocket.py           # WS /ws/alerts
│   │       └── __init__.py
│   │
│   ├── README.md                      # Backend-specific docs
│   ├── insert_test_mule.py            # Blockchain test script
│   ├── test_ingest_dummy.py           # Ingest pipeline test
│   └── scripts/
│       ├── create_demo_users.py       # Populate test users
│       ├── deploy_contract.py         # Smart contract deployment
│       └── seed_atms.py               # Seed test ATM data
│
├── blockchain/                        # Ganache + Solidity
│   ├── package.json
│   ├── .env                           # GANACHE_RPC_URL, etc.
│   ├── config.yaml                    # Contract address, ABI path
│   ├── hardhat.config.js              # Hardhat config
│   ├── blockchain_service.py          # Web3.py contract interface
│   ├── blockchain_api.py              # FastAPI wrapper (port 8001)
│   ├── deploy.py                      # Automated deployment
│   ├── README.md                      # Blockchain-specific docs
│   ├── contracts/
│   │   ├── MuleAccountRegistry.sol    # Smart contract (Keccak-256 hashing)
│   │   └── deployed_address.json      # Saved address after deploy
│   ├── artifacts/
│   │   └── contracts/
│   │       └── MuleAccountRegistry.sol/
│   │           └── MuleAccountRegistry.json  # Compiled ABI
│   ├── scripts/
│   │   ├── deploy.js                  # Hardhat deploy
│   │   └── testContract.js            # Manual contract testing
│   ├── test/
│   │   └── Lock.js                    # Hardhat test suite
│   └── ignition/
│       └── modules/                   # Hardhat Ignition modules
│
├── database/                          # PostgreSQL setup
│   ├── schema.sql                     # Tables, triggers, indexes
│   ├── README.md                      # Database-specific docs
│   ├── generate_data.py               # Synthetic complaint generation
│   ├── insert_atms_*.py               # District-specific ATM scripts
│   ├── insert_atms.py                 # Main ATM insert script
│   └── atm_inserts/
│       └── all_cities.sql             # Compiled ATM insert SQL
│
├── ML/                                # XGBoost model
│   ├── train_model.py                 # Model training script
│   ├── model.pkl                      # Trained model artifact
│   ├── requirements.txt
│   ├── README.md                      # ML-specific docs
│   └── generate_data.py               # Complaint data generation
│
└── security/                          # Security documentation
    ├── 00-overview.md                 # Security module overview
    ├── 01-security-objective.md
    ├── 02-day-1-scope.md
    ├── 03-security-principles.md
    ├── 04-current-integration-decisions.md
    ├── 05-day-1-status.md
    ├── 06-jwt-authentication-token-security.md
    ├── 07-rbac-jurisdiction-scoped-authorization.md
    ├── 08-rate-limiting-api-abuse-protection.md
    ├── 09-pii-protection-data-privacy.md
    ├── 10-audit-logging-security-events.md
    ├── 11-testing-evidence.md
    └── README.md
```

---

## AI / Machine Learning

### Model Architecture

CyberSight uses an **XGBoost district classifier** to predict the withdrawal district from a fraud complaint.

**Approach:**
- **Option A** (rejected): Direct coordinate regression → 75km MAE (withdrawal coordinates were randomly generated, no learnable signal)
- **Option B** (chosen): Predict withdrawal district → rank Top-5 ATMs from predicted district via spatial lookup

### Training Data

- **Dataset:** 419,863 synthetic complaints generated from PostgreSQL
- **Features:** 19 real-time features (see below)
- **Target:** Withdrawal district (10 classes: Agra, Bengaluru, Delhi, Delhi NCR, Hyderabad, Jamtara, Lucknow, Mumbai, Patna, Pune)
- **Train/Test Split:** 80/20

### 19 Features (Exact Training Order)

| Position | Feature | Type | Source | Notes |
|----------|---------|------|--------|-------|
| 1 | `fraud_type_enc` | int (encoded) | Input | LabelEncoder: UPI Fraud, Card Fraud, Online Banking, etc. |
| 2 | `amount_lost` | float | Input | Amount of money lost (₹) |
| 3 | `number_of_hops` | int | Input | Count of intermediary accounts |
| 4 | `victim_lat` | float | Input | Victim location latitude |
| 5 | `victim_lon` | float | Input | Victim location longitude |
| 6 | `bank_enc` | int (encoded) | Input | LabelEncoder: SBI, HDFC, ICICI, etc. (8 banks) |
| 7 | `account_age_days` | int | Computed | Default 180 (not available at complaint time) |
| 8 | `mule_network_flag` | int (0/1) | Computed | 1 if number_of_hops ≥ 4, else 0 |
| 9 | `is_festival_period` | int (0/1) | Hardcoded | Always 0 (festival dates are 2024-only; demo is 2026) |
| 10 | `hour_of_day_sin` | float | Computed | sin(π × hour / 12) — cyclical encoding of complaint hour |
| 11 | `hour_of_day_cos` | float | Computed | cos(π × hour / 12) — cyclical encoding of complaint hour |
| 12 | `day_of_week` | int (0-6) | Computed | 0 = Monday, 6 = Sunday |
| 13 | `is_weekend` | int (0/1) | Computed | 1 if day_of_week >= 5 |
| 14 | `rolling_6h_complaint_count` | int | DB Query | Count of complaints in victim's district in past 6 hours |
| 15 | `district_risk_score` | float (0-1) | DB Query | Average risk score from all complaints in victim's district |
| 16 | `atm_density` | int | PostGIS Query | Count of ATMs within 5km radius of victim location |
| 17 | `time_since_last_complaint_same_bank` | float | DB Query | Hours since last complaint from same beneficiary bank (-1 if none) |
| 18 | `victim_to_withdrawal_distance_km` | float | Default 0.0 | Unknown at inference time; set to 0.0 |
| 19 | `district_enc` | int (encoded) | Input | LabelEncoder: victim district (INPUT only) |

### Model Performance

| Metric | Value |
|--------|-------|
| Naive Baseline | 26.9% (always predict most common district, Delhi NCR) |
| **Top-1 Accuracy** | **90.0%** |
| Top-3 Accuracy | 100.0% |
| Top-5 Accuracy | 100.0% |
| **Improvement over Baseline** | **+63.1 percentage points** |
| Inference Latency | 9.76 ms |

### Inference-Time Feature Decisions

| Feature | Value | Reason |
|---------|-------|--------|
| `account_age_days` | 180 (default) | Account age not available at complaint submission |
| `mule_network_flag` | Derived from complaint | 1 if number_of_hops ≥ 4; embedded in complaint data |
| `is_festival_period` | 0 (hardcoded) | Festival dates in training data are 2024-only; demo system is 2026 |
| `atm_density` | PostGIS 5km radius query | Real-time computed from victim's location |
| `district_risk_score` | DB query (AVG from complaints) | Parameterized; reflects current district risk |
| `time_since_last_complaint_same_bank` | DB query (-1 if none) | Hours elapsed; -1 if no prior complaint from same bank |
| `victim_to_withdrawal_distance_km` | 0.0 | Unknown at inference time; withdrawal location is being predicted |

### Model Artifact (`model.pkl`)

The `ML/model.pkl` file contains:

| Key | Type | Description |
|-----|------|-------------|
| `model` | XGBClassifier | Trained model object |
| `features` | list[str] | 19-feature names in exact order |
| `le_fraud` | LabelEncoder | Fraud type encoder (INPUT) |
| `le_bank` | LabelEncoder | Bank name encoder (INPUT) |
| `le_district` | LabelEncoder | Victim district encoder (INPUT only) |
| `le_target` | LabelEncoder | Withdrawal district decoder (OUTPUT only) |
| `atm_df` | DataFrame | ATM lookup table: columns `[atm_id, district, bank_name, lon, lat]` |
| `naive_baseline` | float | Baseline accuracy (0.269) |
| `shap_importance` | dict | Feature importance scores |
| `district_classes` | list[str] | All withdrawal district labels |

**Critical Note:** `le_district` encodes the **INPUT** feature (victim's district). `le_target` decodes the **OUTPUT** prediction (predicted withdrawal district). These must never be mixed.

### Novel Gate: Low-Confidence Suppression

- If model confidence < 0.4 → Prediction status = `ANALYST_REVIEW`
- Auto-dispatch is suppressed; prediction still logged for analyst review
- Ensures uncertain predictions do not trigger false-positive alerts

### SHAP Explainability

Per inference, the backend computes SHAP values using `TreeExplainer`:

- **Format:** dict of `{feature_name: shap_value}`
- **Interpretation:** Positive = increases predicted risk; negative = decreases risk
- **Storage:** Stored as JSONB in `predictions.shap_values`
- **Frontend:** Interactive SHAP chart shows top 3–5 features driving the prediction

### Setup

```bash
cd ML
pip install -r requirements.txt
python train_model.py
```

The trained `model.pkl` is saved to `ML/model.pkl` and loaded by the backend at startup.

---

## Backend

### Framework & Runtime

- **Framework:** FastAPI (async, type-safe, auto-docs)
- **Runtime:** Python 3.11
- **Server:** Uvicorn (ASGI)
- **Rate Limiting:** SlowAPI (per-IP)
- **Database ORM:** SQLAlchemy 2.0 (async-ready)
- **Authentication:** JWT + Passlib + Bcrypt

### Core Endpoints

#### Authentication

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| POST | `/api/auth/login` | username, password | `{access_token: str, token_type: str}` | Rate-limited; 5 attempts/IP/window |

#### Complaint Ingestion & Prediction

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| POST | `/api/complaints/ingest` | Complaint data (fraud_type, amount, beneficiary_account, victim_lat/lon, etc.) | `{complaint_id, tracking_number, prediction: {district, top_5_atms, confidence, risk_level}, alert_level, shap_values}` | Full pipeline: validate → fraud detect → predict → dispatch |
| POST | `/api/predict` | 19-feature vector | `{predicted_district, top_5_atms, confidence, shap_values}` | Direct ML inference (bypass ingest) |

#### Investigation & Evidence

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| GET | `/api/complaints` | Query params: district, status, date_range | List of complaints | Jurisdiction-scoped |
| GET | `/api/complaints/{id}` | — | Complaint + prediction + top 5 ATMs | Full details |
| POST | `/api/complaints/{id}/notes` | note_text, officer_id (from JWT) | `{id, created_at, author}` | Case investigation notes |
| GET | `/api/complaints/{id}/notes` | — | List of notes | Reverse chronological |
| POST | `/api/complaints/{id}/actions` | action_type, details | `{id, created_at, officer_id}` | Action log (CCTV review, ATM visit, etc.) |
| GET | `/api/complaints/{id}/actions` | — | List of actions | Timeline of investigator actions |

#### Mule Registry & Blockchain

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| GET | `/api/mule/registry` | Query: risk_level, date_range | List of flagged accounts | Blockchain-backed |
| GET | `/api/mule/registry/{account_hash}` | — | Account details + blockchain proof (tx_hash, block timestamp) | On-chain verification |
| POST | `/api/mule/flag` | beneficiary_account, risk_score, reason | `{tx_hash, block_number}` | Flag account on blockchain (HIGH alerts trigger this automatically) |

#### Heatmap & Analytics

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| GET | `/api/heatmap` | Query: date_range, district, fraud_type, risk_level | GeoJSON FeatureCollection | District-level choropleth + ATM points |
| GET | `/api/reports` | Query: report_type (district, bank, fraud_type), format (json or csv) | Aggregated statistics + CSV (if format=csv) | Export-ready |

#### Real-Time Alerts

| Method | Endpoint | Request | Response | Notes |
|--------|----------|---------|----------|-------|
| WS | `/ws/alerts` | (WebSocket upgrade) | `{alert_id, complaint_id, risk_level, prediction, timestamp}` | JWT auth on upgrade; 4001 close-code if token invalid |

### Middleware & Security

| Middleware | Purpose | Implementation |
|-----------|---------|-----------------|
| **JWT Verification** | Validate access tokens on every request | SHA-256 token hash lookup in `revoked_tokens` table; reject if expired or revoked |
| **CORS** | Allow cross-origin requests | `allow_origins=["http://localhost:5173"]` (frontend URL) |
| **Rate Limiting (SlowAPI)** | Prevent brute-force / DOS | 5 failed login attempts/IP → 429; per-endpoint limits configurable |
| **RBAC + Jurisdiction Scoping** | Enforce authorization | Middleware checks JWT `role` + `jurisdiction` claims before accessing complaint/prediction data |
| **OPTIONS Preflight Exemption** | Allow CORS preflight | OPTIONS requests bypass JWT checks (browser requirement) |

### Error Handling

| Scenario | Response | Status | Notes |
|----------|----------|--------|-------|
| Invalid JWT | `{"detail": "Not authenticated"}` | 401 | Token expired, revoked, or missing |
| Missing jurisdiction | `{"detail": "Unauthorized"}` | 403 | Officer can only see own district complaints |
| Complaint not found | `{"detail": "Not found"}` | 404 | Complaint ID invalid or not in officer's jurisdiction |
| Rate limit exceeded | `{"detail": "Rate limit exceeded"}` | 429 | Too many requests; retry after cooldown |
| ML model unavailable | `{"detail": "Prediction service unavailable"}` | 503 | Model not loaded or inference failed |
| Blockchain down | Ingest still returns 200 | 200 | Non-blocking; HIGH alerts log blockchain call but don't block |
| Validation error | `{"detail": "Invalid input: ..."}` | 400 | Null bytes, length overflow, etc. |

### ML Integration

- **Model Loading:** `XGBoost + encoders + ATM dataframe` loaded once at startup from `ML/model.pkl`
- **Feature Contract:** Exact 19-feature order enforced; any deviation raises `FeatureOrderMismatch`
- **Inference:** Synchronous per-request; 9.76ms average latency
- **SHAP Values:** Computed per prediction; JSON-serialized into database
- **Confidence Gate:** < 0.4 → `ANALYST_REVIEW` status; no auto-dispatch

### Database Interaction

- **Connection Pooling:** SQLAlchemy connection pool (default 5 connections)
- **Jurisdiction Scoping:** Cyber Cell Officers can only query complaints from their `jurisdiction_district`
- **PostGIS Queries:** ATM density computed via ST_DWithin (5km radius from victim)
- **Audit Trail:** Every sensitive action (login, evidence write, blockchain flag) recorded in `audit_log`

### Startup & Dependencies

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Requires:
- PostgreSQL 15 on port 5433
- ML/model.pkl accessible
- .env file with DATABASE_URL, SECRET_KEY, GANACHE_URL

---

## Database

### Technology & Setup

- **Engine:** PostgreSQL 15
- **Spatial:** PostGIS 3.6.2
- **Port:** 5433 (non-standard; adjust in .env)
- **Database:** `cybersight`

### Schema Overview

#### Core Tables

| Table | Rows | Purpose |
|-------|------|---------|
| `users` | ~5 | Authentication; 3 roles + jurisdiction/bank scoping |
| `complaints` | 419,863 | Core NCRP complaint records + 28 ML features |
| `atm_locations` | 4,625 | Real ATM coordinates (PostGIS POINT geometry) |
| `predictions` | ~419,863 | ML output: top 5 ATMs, confidence, SHAP values, risk level |
| `dispatch_log` | Variable | 4-channel alert delivery status (SMS, Email, Webhook, Dashboard) |
| `mule_accounts` | Variable | Flagged beneficiary accounts |
| `case_notes` | Variable | Investigator notes per complaint |
| `action_log` | Variable | Officer actions per complaint (CCTV review, ATM visit, etc.) |
| `audit_log` | Variable | System-wide sensitive action audit trail |
| `registry_provenance` | Variable | Blockchain provenance: account_hash, tx_hash, flagging_authority, evidence_basis, block_timestamp |
| `keyword_fraud_map` | ~50 | Keyword → fraud type mapping |
| `revoked_tokens` | Variable | Blacklisted JWT tokens (for logout) |

#### Key Columns

**users**
```sql
id (PK)
username (UNIQUE)
password_hash
role (CHECK: admin, cyber_cell_officer, bank_nodal_officer)
jurisdiction_district (scoping for cyber_cell_officer)
bank_name (scoping for bank_nodal_officer)
created_at
```

**complaints**
```sql
id (PK)
complaint_id (UNIQUE)
tracking_number (UNIQUE, auto-generated: CS-2026-XXXXXXX)

-- Input fields
fraud_type
fraud_keywords (TEXT[])
victim_district, victim_state, victim_lat, victim_lon
victim_location (GEOMETRY Point, 4326)
amount_lost, transaction_amount, transaction_timestamp
victim_account_type, beneficiary_account_type
beneficiary_account, beneficiary_bank, upi_id, mobile_number
number_of_hops
alert_level (LOW, MEDIUM, HIGH)
status (pending, prediction_failed, analyst_review, flagged, resolved)

-- Computed features (28 total)
rolling_6h_complaint_count, district_risk_score, atm_density
time_since_last_complaint_same_bank, mule_network_flag
is_festival_period, hour_of_day_sin, hour_of_day_cos
day_of_week, is_weekend, account_age_days
victim_to_withdrawal_distance_km
(+ others)

created_at
```

**predictions**
```sql
id (PK)
complaint_id (FK → complaints)
predicted_district
top_5_atms (JSON array)
confidence (float 0-1)
risk_level (LOW, MEDIUM, HIGH)
shap_values (JSONB: {feature: value})
freezable_amount (amount_lost × 0.6)
created_at
```

**mule_accounts**
```sql
id (PK)
beneficiary_account
beneficiary_bank
account_hash (Keccak-256, from blockchain)
risk_score
flagging_authority (e.g., "Delhi Cyber Cell")
evidence_basis (INVESTIGATION_VERIFIED, MONITORING_SUSPECTED)
tx_hash (blockchain transaction hash)
block_timestamp (from blockchain)
created_at
```

**atm_locations**
```sql
id (PK)
atm_id (UNIQUE: e.g., DEL00001)
district
bank_name
lon, lat
location (GEOMETRY Point, 4326)
created_at
```

Indexes:
- GIST on `location` for fast radius queries
- B-tree on `district`, `bank_name`

#### ATM Data

| District | Count | Source |
|----------|-------|--------|
| Bengaluru | 1,137 | Overpass Turbo + OpenStreetMap |
| Delhi NCR | 869 | Overpass Turbo + OpenStreetMap |
| Delhi | 797 | Overpass Turbo + OpenStreetMap |
| Hyderabad | 566 | Overpass Turbo + OpenStreetMap |
| Pune | 457 | Overpass Turbo + OpenStreetMap |
| Mumbai | 300 | Overpass Turbo + OpenStreetMap |
| Jamtara | 300 | Synthetic (correct bounding box) |
| Patna | 89 | Overpass Turbo + OpenStreetMap |
| Lucknow | 57 | Overpass Turbo + OpenStreetMap |
| Agra | 53 | Overpass Turbo + OpenStreetMap |
| **Total** | **4,625** | — |

### Triggers & Constraints

| Trigger | Purpose |
|---------|---------|
| `trg_tracking_number` | Auto-generates tracking number (CS-YYYY-XXXXXXX) on INSERT |
| `trg_audit_log_on_delete` | Logs all deletes to audit_log for compliance |

### Enforcement

- **Foreign Keys:** Enabled; referential integrity enforced
- **Role CHECK:** users.role must be one of 3 valid values
- **Alert Level CHECK:** complaints.alert_level must be LOW, MEDIUM, or HIGH
- **Unique Constraints:** complaint_id, tracking_number, atm_id, username

### Setup

```bash
# Create database
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE cybersight;"

# Enable PostGIS & pgcrypto
psql -h localhost -p 5433 -U postgres -d cybersight \
  -c "CREATE EXTENSION postgis; CREATE EXTENSION pgcrypto;"

# Run schema
psql -h localhost -p 5433 -U postgres -d cybersight -f database/schema.sql

# Seed ATMs
psql -h localhost -p 5433 -U postgres -d cybersight -f database/atm_inserts/all_cities.sql

# Insert demo users
psql -h localhost -p 5433 -U postgres -d cybersight << EOF
INSERT INTO users (username, password_hash, role, jurisdiction_district, bank_name)
VALUES
  ('cyber_delhi', '<bcrypt>', 'cyber_cell_officer', 'Delhi', NULL),
  ('i4c_admin', '<bcrypt>', 'admin', NULL, NULL),
  ('bank_sbi', '<bcrypt>', 'bank_nodal_officer', NULL, 'SBI');
EOF
```

---

## Blockchain

### Problem Solved

Traditional complaint databases allow privileged insiders to modify, delete, or manipulate records. Blockchain's immutable ledger ensures verified mule accounts cannot be altered or erased, providing:

- **Tamper Resistance:** Recorded accounts cannot be unilaterally modified
- **Audit Trail:** Complete history of who flagged an account, when, and why
- **Transparency:** All agencies can query the same truth source
- **Trust:** No single agency can erase evidence

### Smart Contract: MuleAccountRegistry

**Location:** `blockchain/contracts/MuleAccountRegistry.sol`  
**Network:** Ganache (local Ethereum testnet)  
**Language:** Solidity 0.8.20

#### Key Features

| Feature | Implementation |
|---------|-----------------|
| **Account Hashing** | Keccak-256 hash of account ID; plaintext never stored on-chain |
| **Owner-Only Control** | `onlyOwner` modifier; contract deployer is sole flagging authority |
| **Stored Metadata** | Risk score (uint256), timestamp (block.timestamp), reason (string), flagging authority (string), evidence basis (string) |
| **Verification Gate** | Evidence basis must be one of: "INVESTIGATION_VERIFIED", "MONITORING_SUSPECTED" |
| **Event Logging** | `AccountFlagged` and `AccountUnflagged` events indexed for efficient queries |
| **Unflagging** | Owner can unflag accounts if investigation is reversed |

#### Data Structure

```solidity
struct MuleAccount {
    bool flagged;
    uint256 riskScore;
    uint256 timestamp;
    string reason;
    string flaggingAuthority;
    string evidenceBasis;
}

mapping(bytes32 => MuleAccount) private muleAccounts;
```

**On-Chain Storage:**
- `accountHash` (bytes32, KECCAK-256) — indexed for efficient lookup
- `flagged` (bool) — current status
- `riskScore` (uint256) — 0–100
- `timestamp` (uint256) — block.timestamp (immutable proof of when flagging occurred)
- `reason` (string) — human-readable reason for flagging
- `flaggingAuthority` (string) — e.g., "Delhi Cyber Cell"
- `evidenceBasis` (string) — must be INVESTIGATION_VERIFIED or MONITORING_SUSPECTED

#### Core Functions

| Function | Signature | Access | Purpose |
|----------|-----------|--------|---------|
| `flagAccount` | `flagAccount(string accountId, uint256 riskScore, string reason, string flaggingAuthority, string evidenceBasis)` | Owner-only | Flag a mule account; emits `AccountFlagged` |
| `unflagAccount` | `unflagAccount(string accountId)` | Owner-only | Remove flag if investigation is reversed |
| `isAccountFlagged` | `isAccountFlagged(string accountId)` | Public | Check if account is flagged (returns bool) |
| `getAccountDetails` | `getAccountDetails(string accountId)` | Public | Retrieve full MuleAccount struct (if flagged) |

#### Events

```solidity
event AccountFlagged(
    bytes32 indexed accountHash,
    uint256 riskScore,
    uint256 timestamp,
    string flaggingAuthority,
    string evidenceBasis
);

event AccountUnflagged(
    bytes32 indexed accountHash,
    uint256 timestamp
);
```

### Backend Integration

**Location:** `blockchain/blockchain_service.py`, `blockchain/blockchain_api.py`  
**Wrapper Service:** FastAPI on `localhost:8001` (separate from main backend on 8000)

#### Deployment

1. **Compile:** `npm run compile` → generates ABI in `artifacts/`
2. **Deploy:** `python deploy.py` → deploys to Ganache, saves address to `config.yaml`
3. **Service Start:** `python blockchain/blockchain_api.py` → wraps contract in REST API

#### Runtime Flow

When ingest detects HIGH risk:

```
Backend (8000)
    │
    └─► POST http://localhost:8001/flag_mule
            │
            ├─► Load Web3 connection (Ganache)
            ├─► Hash account ID (Keccak-256)
            ├─► Call flagAccount(...) on contract
            ├─► Wait for tx receipt (timeout: 10s)
            └─► Return tx_hash to backend
                    │
                    └─► Backend logs tx_hash to DB
                        (Non-blocking: ingest still returns 200)
```

**Graceful Degradation:** If Ganache is down, blockchain call times out or fails; ingest still returns 200 OK (alert dispatch proceeds, blockchain flagging deferred).

### Network Configuration

**Ganache RPC URL:** `http://127.0.0.1:7545`  
**Chain ID:** 5777 (Ganache default)  
**Network Type:** Private (localhost only)  
**Block Time:** Instant (no mining delay)

**Contract Address** (after deploy):
```yaml
contract:
  address: '0x909457ddC90cd429C140027ea776d070cD99137a'
```

### Setup

```bash
cd blockchain

# Compile Solidity
npm run compile

# Deploy to Ganache (must be running)
python deploy.py

# Start blockchain API wrapper
python blockchain_api.py
```

**Prerequisites:**
- Ganache running on `http://127.0.0.1:7545`
- Node.js + npm
- Python 3.11 + `pip install -r requirements.txt`

---

## Frontend

### Framework & Stack

- **UI Framework:** React 18.3.1
- **Language:** TypeScript 5.5.3
- **Build Tool:** Vite 5.4.2
- **Styling:** TailwindCSS 3.4.1
- **Routing:** React Router 6.30.6
- **State Management:** React Context API (AuthContext, SocketContext)
- **HTTP Client:** Axios
- **WebSocket:** Socket.IO Client 4.8.3
- **Maps:** Leaflet 1.9.4 + React-Leaflet
- **Charts:** Recharts 2.15.4 (SHAP charts, reports)
- **Icons:** Lucide React 0.446.0

### Pages & Features

#### Login Page
- Username/password form
- JWT token storage (localStorage)
- Redirect to dashboard on success
- Rate-limited error feedback

#### Role-Based Dashboards
Each role has a distinct primary view:

**Cyber Cell Officer Dashboard**
- Jurisdiction-scoped complaint list (own district only)
- Alert live feed (WebSocket)
- Complaint drill-down: prediction + Top-5 ATMs + SHAP explanation
- HeatmapPage access (district-level risk)
- Evidence/notes entry
- Mule registry (own district)

**Bank Nodal Officer Dashboard**
- Bank-scoped complaints (own bank's transactions)
- Freeze/action buttons (non-functional in demo; integration pending)
- Alert dispatch status (SMS/Email/Webhook/Dashboard)
- Reports (bank-wise analytics)

**I4C Admin Dashboard**
- Cross-jurisdictional oversight
- All complaints + predictions
- System-wide statistics
- Access to all blockchain records
- Full reports + export
- User management (future scope)

#### HeatmapPage
- Leaflet map with PostGIS-backed district choropleth
- Color-coding: GREEN (LOW), YELLOW (MEDIUM), RED (HIGH)
- Filter bar: date range, district, fraud type, risk level
- Click district → drill-down to Top-5 ATMs (ranked by prediction)
- ATM cluster view with risk scores

#### AlertsPage
- Real-time WebSocket feed
- Severity-coded rows (RED for HIGH, YELLOW for MEDIUM)
- Each alert shows: complaint ID, victim location, amount, predicted ATM district, risk level
- Click alert → AlertDetailPage

#### AlertDetailPage
- Full complaint details
- ML prediction + confidence
- SHAP chart (top features)
- Top-5 ATMs with coordinates + risk scores
- Evidence panel (notes + actions)
- Action buttons: "Review Evidence", "Flag on Blockchain" (if HIGH)

#### MuleRegistryPage
- Table of flagged accounts
- Columns: account (obfuscated), risk score, flagging authority, evidence basis, blockchain tx hash, block timestamp
- Click row → blockchain verification proof (transaction details from Ganache)
- Filter: date range, risk level

#### BlockchainLogPage
- Timeline of AccountFlagged + AccountUnflagged events
- Filters: date range, flagging authority
- Shows on-chain proof (tx hash, block number, timestamp)

#### ReportsPage
- **District-wise:** complaints, HIGH alerts, average risk score by district
- **Bank-wise:** complaints, average amount by bank, fraud type breakdown
- **Fraud-typology-wise:** count by fraud type, average amount, top ATM clusters
- CSV export button → downloads aggregated data

#### DispatchLogPage
- 4-channel status: SMS, Email, Webhook, Dashboard
- Rows: alert, channel, status (Sent/Failed/Pending), timestamp
- Filter: date range, status, channel

#### SettingsPage
- User preferences (theme, refresh rate, language)
- Placeholder for future personalization

### Real-Time Architecture

#### AuthContext
- Manages JWT token (localStorage)
- Provides `useAuth()` hook for token + user role/jurisdiction
- Handles logout (token revocation)

#### SocketContext
- Maintains WebSocket connection to `/ws/alerts`
- JWT sent on connection upgrade
- Handles 4001 close-code (token expired)
- Auto-reconnects on failure
- Broadcasts alerts to all components subscribing to `useSocket()`

#### ProtectedRoute Component
- Wraps routes requiring authentication
- Checks JWT validity + role + jurisdiction
- Redirects to `/login` if unauthorized
- Supports `allowedRoles` prop for role-gating

### State Management

**Client-Side:**
- AuthContext: user identity, JWT, role
- SocketContext: real-time alert stream
- Component state: local UI state (filters, pagination, modals)
- LocalStorage: JWT, user preferences

**Server-Side (Backend):**
- PostgreSQL: persistent state (complaints, predictions, audit logs)
- Ganache blockchain: immutable mule registry

### Error Handling & Fallbacks

| Scenario | Behavior |
|----------|----------|
| Backend unreachable | Mock data fallback; "cached data" banner auto-hides when live |
| WebSocket disconnected | Show disconnection indicator; allow non-real-time browsing; auto-reconnect |
| JWT expired | Redirect to login; prompt for re-authentication |
| Insufficient permissions | Show "Access Denied"; offer jurisdiction/role clarification |
| Blockchain unavailable | Alert flagging deferred; complaint still processed |

### Setup & Development

```bash
cd frontend

npm install
npm run dev   # Start dev server on http://localhost:5173
```

### Build

```bash
npm run build    # Production bundle in dist/
npm run preview  # Test production build locally
```

---

## Security

### Implemented Mechanisms

#### 1. JWT Authentication & Token Security

- **Algorithm:** HS256 (HMAC-SHA256)
- **Claims:** `sub` (username), `role`, `jurisdiction`, `bank_name`, `exp` (expiration)
- **Expiration:** 8 hours (configurable)
- **Token Storage:** LocalStorage (frontend) — CSRF risk noted; mitigated by SameSite cookies (future)
- **Token Revocation:** On logout, token hash (SHA-256) added to `revoked_tokens` blacklist; checked on every request
- **Refresh Logic:** Each login issues new access token; no separate refresh token (future scope)

#### 2. Role-Based Access Control (RBAC)

**Three Roles:**
- `admin` — Full system access; no jurisdiction/bank restrictions
- `cyber_cell_officer` — District-scoped; can only view complaints from assigned `jurisdiction_district`
- `bank_nodal_officer` — Bank-scoped; can only view complaints involving assigned `bank_name`

**Enforcement:** Middleware checks JWT `role` + `jurisdiction` claims before authorizing DB queries. Query filters applied at ORM level (SQLAlchemy).

#### 3. Data Access Control

| User Type | Can Access | Cannot Access |
|-----------|-----------|---------------|
| Cyber Cell (Delhi) | Complaints from Delhi district | Complaints from other districts |
| Bank Nodal (SBI) | Transactions involving SBI | Transactions involving other banks |
| I4C Admin | All complaints, all districts | (Full access) |

#### 4. Account Identifier Protection (Blockchain)

- **Plaintext Never On-Chain:** Account IDs are hashed (Keccak-256) before blockchain storage
- **Backend Hashing:** MuleAccountRegistry contract handles hashing; backend sends plaintext account ID to contract, contract hashes it
- **Audit Trail:** Hash + risk score + flagging authority + evidence basis stored immutably
- **PII Isolation:** Plaintext accounts stored only in PostgreSQL `mule_accounts` table (not readable by external systems without credentials)

#### 5. Input Validation

| Check | Purpose | Implementation |
|-------|---------|-----------------|
| Null byte rejection | Prevent SQL injection | `validate_text()` function checks for `\x00` |
| Length limits | Prevent DOS via huge payloads | Text fields capped at 5,000 characters |
| Duplicate complaint ID | Prevent replay attacks | DB UNIQUE constraint on `complaint_id` |
| SQL parameterization | Prevent SQL injection | SQLAlchemy ORM + parameterized queries |
| Rate limiting | Prevent brute-force | 5 failed login attempts/IP → 429 |

#### 6. Password Security

- **Hashing Algorithm:** Bcrypt (4.0.1)
- **Hash Storage:** `users.password_hash` (salted, iterated)
- **Verification:** Passlib `verify_password()` function
- **Never Logged:** Passwords excluded from audit logs and error messages

#### 7. Audit Logging

All sensitive actions logged to `audit_log` table:

| Action | Logged Fields |
|--------|---------------|
| Login | user_id, timestamp, success/failure, IP address |
| Complaint ingest | user_id, complaint_id, alert_level, ML confidence |
| Blockchain flag | user_id, account_hash, tx_hash, timestamp |
| Evidence write | user_id, complaint_id, note_text, timestamp |
| Token revocation | user_id, token_hash, timestamp |

**Retention:** Indefinite (no auto-purge; compliance responsibility of operators)

#### 8. CORS & Cross-Origin Protection

- **Allowed Origins:** `http://localhost:5173` (frontend URL)
- **Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS
- **Credentials:** Enabled (for JWT in Authorization header)
- **Preflight Handling:** OPTIONS requests bypass JWT checks (browser requirement)

#### 9. Rate Limiting (SlowAPI)

- **Login Endpoint:** 5 failed attempts/IP/window → 429 rate-limit-exceeded
- **Per-Endpoint Limits:** Configurable (default: no limit on other endpoints)
- **Bypass:** Limiter checks IP address; local development can use 127.0.0.1

#### 10. Database Connection Security

- **Connection String:** PostgreSQL URL with password stored in `.env` (not hardcoded)
- **Port:** 5433 (non-standard; reduces default-port scanning risk)
- **SSL/TLS:** Optional (localhost for demo; production would enforce)
- **Connection Pooling:** SQLAlchemy pool_size=5 (limits resource exhaustion)

#### 11. Blockchain-Specific Security

| Measure | Implementation |
|---------|-----------------|
| **Private Network** | Ganache (localhost only); not exposed to internet |
| **Owner Control** | Only contract deployer (owner) can flag accounts |
| **Immutability** | Once flagged, account record cannot be deleted (only unflagged) |
| **Event Logging** | All flags emitted as events; queryable for audit trail |
| **Keccak-256 Hashing** | Industry-standard Ethereum hash; collision-resistant |

### NOT Implemented (Documented for Completeness)

- **SSL/TLS:** localhost demo doesn't require; production would enforce
- **Refresh Tokens:** Single JWT per login (future scope: implement refresh token rotation)
- **HTTPS Only:** Demo uses HTTP; production must enforce HTTPS
- **2FA / MFA:** Not implemented; future scope
- **Encryption at Rest:** Database not encrypted; future scope for production
- **API Key Rotation:** N/A (JWT-based auth only)
- **Secrets Rotation:** Assumes .env is secure (not auto-rotated)

---

## Installation & Setup

### Prerequisites

| Component | Requirement | Install |
|-----------|-------------|---------|
| **Node.js** | 16.x+ | https://nodejs.org/ |
| **Python** | 3.11+ | https://python.org/ |
| **PostgreSQL** | 15.x | https://postgresql.org/ |
| **PostGIS** | 3.6.2+ | (via PostgreSQL extension) |
| **Ganache** | 7.x | `npm install -g ganache` |
| **Git** | Latest | https://git-scm.com/ |

### Step 1: Clone Repository

```bash
git clone https://github.com/anixtm3/cybersight.git
cd cybersight
```

### Step 2: Database Setup

```bash
# Create database
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE cybersight;"

# Enable PostGIS + pgcrypto extensions
psql -h localhost -p 5433 -U postgres -d cybersight << EOF
CREATE EXTENSION postgis;
CREATE EXTENSION pgcrypto;
EOF

# Run schema
psql -h localhost -p 5433 -U postgres -d cybersight -f database/schema.sql

# Seed ATM data (4,625 real ATMs from 10 districts)
psql -h localhost -p 5433 -U postgres -d cybersight -f database/atm_inserts/all_cities.sql

# (Optional) Generate synthetic complaint data
cd database
python generate_data.py
cd ..
```

### Step 3: ML Model Setup

```bash
cd ML

# Install dependencies
pip install -r requirements.txt

# Train model (or use pre-trained model.pkl)
python train_model.py

# Verify model loads
python -c "import pickle; m = pickle.load(open('model.pkl', 'rb')); print(f'Model loaded. Classes: {m[\"district_classes\"]}')"

cd ..
```

**Note:** If `model.pkl` already exists in `ML/`, skip training. Backend loads it on startup.

### Step 4: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5433/cybersight
SECRET_KEY=cybersight-secret-2026-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
GANACHE_URL=http://127.0.0.1:7545
ACCOUNT_HASH_SALT=9957724d3e3a4deb71e3b9abae516163d431d72a040e0345bc493a166add44f4
EOF

cd ..
```

**Important:** Replace `YOUR_PASSWORD` with actual PostgreSQL password.

### Step 5: Blockchain Setup

```bash
cd blockchain

# Install Node dependencies
npm install

# Create .env
cat > .env << EOF
GANACHE_RPC_URL=http://127.0.0.1:7545
EOF

# Compile Solidity contract
npm run compile

cd ..
```

### Step 6: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file (optional; config.ts has defaults)
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
EOF

cd ..
```

### Step 7: Demo Users

Insert demo users into database:

```bash
psql -h localhost -p 5433 -U postgres -d cybersight << 'EOF'
-- Note: In production, use hashed passwords. For demo, use plaintext and hash at first login.
-- For now, use bcrypt hashes. You can generate them with:
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
-- print(pwd_context.hash("password123"))

INSERT INTO users (username, password_hash, role, jurisdiction_district, bank_name)
VALUES
  ('cyber_delhi', '$2b$12$O7/a1TRFEGqxKFzfyLpJoecOGVvg5EhPQ.yHlSvPQi7nkGZdBG1V.', 'cyber_cell_officer', 'Delhi', NULL),
  ('cyber_blr', '$2b$12$O7/a1TRFEGqxKFzfyLpJoecOGVvg5EhPQ.yHlSvPQi7nkGZdBG1V.', 'cyber_cell_officer', 'Bengaluru', NULL),
  ('bank_sbi', '$2b$12$O7/a1TRFEGqxKFzfyLpJoecOGVvg5EhPQ.yHlSvPQi7nkGZdBG1V.', 'bank_nodal_officer', NULL, 'SBI'),
  ('i4c_admin', '$2b$12$O7/a1TRFEGqxKFzfyLpJoecOGVvg5EhPQ.yHlSvPQi7nkGZdBG1V.', 'admin', NULL, NULL);
EOF
```

**Demo Password (all users):** `password123`

---

## Key Performance Numbers

| Metric | Value |
|--------|-------|
| Complaints in training DB | **419,863** |
| ATMs in DB | **4,625** |
| Districts covered | **10** |
| Top-1 Accuracy | **90.0%** |
| Top-3 Accuracy | **100%** |
| Top-5 Accuracy | **100%** |
| Naive baseline (always Delhi NCR) | 26.9% |
| Improvement over baseline | **+63.1 percentage points** |
| ML inference latency | **9.76ms** |
| End-to-end latency | **~200ms** |
| Security tests passing | **34** |
| Confidence threshold for HIGH | ≥ 0.7 |
| Confidence threshold for MEDIUM | ≥ 0.4 |

---

## Districts Covered

Delhi, Delhi NCR, Mumbai, Bengaluru, Hyderabad, Jamtara, Agra, Patna, Pune, Lucknow

---

## Demo Credentials

| Username | Password | Role | Dashboard |
|----------|----------|------|-----------|
| `cyber_delhi` | `password123` | Cyber Cell Officer | Cyber Cell Command Centre |
| `i4c_admin` | `password123` | I4C Admin | I4C Admin Console |
| `bank_sbi` | `password123` | Bank Nodal Officer | Bank Nodal Dashboard |

---

## Startup — All Servers

```powershell
# Terminal 1 — Backend (FastAPI)
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Blockchain API
cd blockchain
uvicorn blockchain_api:app --reload --port 8001

# Terminal 3 — Frontend (React)
cd frontend
npm run dev
# Runs at http://localhost:5173

# Ganache — Open from Start Menu > CyberSight workspace
# Default port: 7545
```

---

## Running the Project

### Step 1: Start Ganache

Open Ganache from Start Menu or run:
```bash
ganache --deterministic --port 7545
```

### Step 2: Deploy Smart Contract

```bash
cd blockchain
python deploy.py
cd ..
```

### Step 3: Start Backend (Terminal 1)

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Backend runs at **http://localhost:8000**  
Auto-docs at **http://localhost:8000/docs**

### Step 4: Start Blockchain API (Terminal 2)

```bash
cd blockchain
python blockchain_api.py
```

Blockchain API runs at **http://localhost:8001**

### Step 5: Start Frontend (Terminal 3)

```bash
cd frontend
npm run dev
```

Frontend runs at **http://localhost:5173**

### Access the Application

- **Frontend:** http://localhost:5173
- **Backend Docs:** http://localhost:8000/docs
- **Ganache Web UI:** http://localhost:7545

---

## Ingest Command (PowerShell)

```powershell
# Step 1: Get token
$login = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/auth/login" `
  -Method POST -ContentType "application/json" `
  -Body '{"username":"cyber_delhi","password":"password123"}' -UseBasicParsing
$token = ($login.Content | ConvertFrom-Json).access_token
$headers2 = @{"Authorization" = "Bearer $token"; "Content-Type" = "application/json; charset=utf-8"}
echo "Token ready"

# Step 2: Ingest complaint (complaint_id must be unique every run)
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/complaints/ingest" `
  -Method POST -Headers $headers2 `
  -Body '{"complaint_id":"DEMO-2026-801","complaint_text":"UPI fraud hua hai","fraud_type":"UPI Fraud","victim_district":"Delhi","victim_state":"Delhi","victim_lat":28.6139,"victim_lon":77.2090,"beneficiary_lat":28.5355,"beneficiary_lon":77.3910,"victim_account_type":"savings","mobile_number":"9876543210","beneficiary_account":"HDFC9876543210","beneficiary_bank":"HDFC","beneficiary_account_type":"savings","transaction_amount":75000,"transaction_timestamp":"2026-08-31T06:00:00.000Z","amount_lost":75000,"number_of_hops":3,"upi_id":"rahul@upi"}' `
  -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Note:** Increment complaint_id each run: 801, 802, 803...

---

## Configuration & Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5433/cybersight

# JWT
SECRET_KEY=cybersight-secret-2026-CHANGE-IN-PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480  # 8 hours

# Blockchain
GANACHE_URL=http://127.0.0.1:7545
ACCOUNT_HASH_SALT=9957724d3e3a4deb71e3b9abae516163d431d72a040e0345bc493a166add44f4

# Logging (optional)
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```bash
# API endpoints (optional; defaults to localhost)
VITE_API_BASE_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

### Blockchain (.env)

```bash
GANACHE_RPC_URL=http://127.0.0.1:7545
```

### Database (.env or environment)

```bash
DB_HOST=localhost
DB_PORT=5433
DB_NAME=cybersight
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
```

---

## API Overview

### Authentication

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "cyber_delhi",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Ingest Complaint & Get Prediction

```http
POST /api/complaints/ingest
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "complaint_id": "TEST-LIVE-003",
  "fraud_type": "UPI_FRAUD",
  "victim_district": "Delhi",
  "victim_state": "Delhi",
  "victim_lat": 28.7041,
  "victim_lon": 77.1025,
  "amount_lost": 50000,
  "beneficiary_account": "9876543210",
  "beneficiary_bank": "SBI",
  "number_of_hops": 3,
  "transaction_timestamp": "2026-01-15T10:30:00Z"
}
```

**Response (200):**
```json
{
  "complaint_id": "TEST-LIVE-003",
  "tracking_number": "CS-2026-0000001",
  "prediction": {
    "predicted_district": "Delhi NCR",
    "top_5_atms": [
      {"atm_id": "DEL00001", "district": "Delhi NCR", "lat": 28.704, "lon": 77.102, "risk_score": 0.85},
      ...
    ],
    "confidence": 0.891,
    "risk_level": "HIGH"
  },
  "alert_level": "HIGH",
  "shap_values": {
    "amount_lost": 0.18,
    "victim_lat": 0.12,
    "victim_lon": -0.09,
    ...
  },
  "blockchain_flag_status": "PENDING"  // Or "SUCCESS" / "FAILED"
}
```

### Get Complaint Details

```http
GET /api/complaints/{complaint_id}
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": 1,
  "complaint_id": "TEST-LIVE-003",
  "tracking_number": "CS-2026-0000001",
  "fraud_type": "UPI_FRAUD",
  "victim_district": "Delhi",
  "amount_lost": "50000.00",
  "alert_level": "HIGH",
  "prediction": {
    "id": 1,
    "predicted_district": "Delhi NCR",
    "confidence": 0.891,
    "risk_level": "HIGH",
    "shap_values": {...},
    "created_at": "2026-01-15T10:30:00Z"
  },
  "created_at": "2026-01-15T10:30:00Z"
}
```

### Get Heatmap Data (GIS)

```http
GET /api/heatmap?date_range=7d&district=Delhi&fraud_type=UPI_FRAUD&risk_level=HIGH
Authorization: Bearer {access_token}
```

**Response (200):** GeoJSON FeatureCollection
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [77.1025, 28.7041]
      },
      "properties": {
        "district": "Delhi",
        "risk_level": "HIGH",
        "complaint_count": 45,
        "avg_risk_score": 0.78
      }
    },
    ...
  ]
}
```

### WebSocket Alerts

```javascript
// Frontend
const socket = io('http://localhost:8000', {
  auth: {
    token: 'eyJhbGciOiJIUzI1NiIs...'
  }
});

socket.on('alert', (data) => {
  console.log('New alert:', data);
  // {
  //   alert_id: 123,
  //   complaint_id: "TEST-LIVE-003",
  //   risk_level: "HIGH",
  //   prediction: { predicted_district: "Delhi NCR", ... },
  //   timestamp: "2026-01-15T10:30:00Z"
  // }
});
```

### Flag Account on Blockchain

```http
POST /api/mule/flag
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "beneficiary_account": "9876543210",
  "beneficiary_bank": "SBI",
  "risk_score": 85,
  "reason": "Confirmed mule account from complaint TEST-LIVE-003",
  "evidence_basis": "INVESTIGATION_VERIFIED"
}
```

**Response (200):**
```json
{
  "id": 1,
  "account_hash": "0x7f5e9c...",
  "tx_hash": "0xabc123...",
  "block_number": 42,
  "block_timestamp": "2026-01-15T10:30:00Z",
  "status": "SUCCESS"
}
```

### Get Reports

```http
GET /api/reports?report_type=district&format=json
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "report_type": "district",
  "generated_at": "2026-01-15T10:35:00Z",
  "data": [
    {
      "district": "Delhi",
      "complaint_count": 1205,
      "high_risk_alerts": 342,
      "avg_amount_lost": 45000,
      "top_fraud_type": "UPI_FRAUD"
    },
    ...
  ]
}
```

**CSV Export:**
```http
GET /api/reports?report_type=district&format=csv
Authorization: Bearer {access_token}
```

Returns CSV file for import into Excel/analytics tools.

---

## Testing & Validation

### Unit Tests

**Backend:**
```bash
cd backend
pytest tests/ -v
```

**Frontend:**
```bash
cd frontend
npm run test
```

### Integration Tests

**Ingest Pipeline:**
```bash
cd backend
python test_ingest_dummy.py
```

Tests the full complaint ingest → ML prediction → dispatch flow.

**Blockchain Contract:**
```bash
cd blockchain
npm run test-contract
```

Tests MuleAccountRegistry contract functions (flag, unflag, verify).

### Manual Verification

**1. Login & Authentication**
- Navigate to http://localhost:5173
- Login with `cyber_delhi` / `password123`
- Verify JWT token in browser DevTools → Storage → LocalStorage
- Verify role-based dashboard (Cyber Cell view)

**2. Submit a Complaint**
```bash
curl -X POST http://localhost:8000/api/complaints/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "complaint_id": "TEST-001",
    "fraud_type": "UPI_FRAUD",
    "victim_district": "Delhi",
    "victim_lat": 28.7041,
    "victim_lon": 77.1025,
    "amount_lost": 50000,
    "beneficiary_account": "9876543210",
    "beneficiary_bank": "SBI",
    "number_of_hops": 3
  }'
```

Expected response: 200 OK + prediction with Top-5 ATMs.

**3. Verify ML Prediction**
- Check `predicted_district` matches one of 10 training districts
- Check `confidence` is 0.0–1.0
- Check `shap_values` are non-null JSON
- Check `top_5_atms` has exactly 5 ATMs from predicted district

**4. Check WebSocket Alerts**
- Open browser console
- If alert_level is MEDIUM/HIGH, should see broadcast in console
- Verify alert data matches complaint

**5. Verify Blockchain Flagging**
- Submit complaint with HIGH risk
- Wait 2–3 seconds (async blockchain call)
- Check Ganache Web UI (http://localhost:7545) → Transactions
- Should see `flagAccount` transaction
- Verify MuleAccountRegistry contract state shows flagged account hash

**6. Jurisdiction Scoping**
- Login as `cyber_delhi`
- Should see only Delhi district complaints
- Login as `i4c_admin`
- Should see all districts
- Login as `bank_sbi`
- Should see only SBI transactions

---

## Blockchain Architecture (Detailed)

### Deployment Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. Developer runs: npm run compile                                   │
│    → Hardhat compiles MuleAccountRegistry.sol                        │
│    → Generates artifacts/contracts/.../MuleAccountRegistry.json (ABI)│
└────────────────────┬─────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 2. Developer runs: python deploy.py                     │
│    → Connects to Ganache (http://127.0.0.1:7545)        │
│    → Deploys bytecode to chain                          │
│    → Saves contract address to config.yaml              │
│    → Prints: "Contract deployed at 0x..."               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ 3. Backend service loads contract                       │
│    → Reads config.yaml (contract address)               │
│    → Loads ABI from artifacts                           │
│    → Creates Web3 contract instance                     │
│    → Ready to accept flag/unflag calls                  │
└─────────────────────────────────────────────────────────┘
```

### On-Chain Flagging Flow

```
Backend receives HIGH-risk complaint
    │
    ├─► Extract beneficiary_account from complaint
    ├─► Compute 19 ML features
    ├─► Call XGBoost prediction
    ├─► Classify risk level = HIGH
    │
    └─► (Non-blocking async) POST to blockchain_api (port 8001):
            {
              beneficiary_account: "9876543210",
              risk_score: 85,
              reason: "Complaint TEST-003",
              flagging_authority: "Delhi Cyber Cell",
              evidence_basis: "INVESTIGATION_VERIFIED"
            }
            │
            ├─► blockchain_api.py receives request
            ├─► Calls Web3 contract instance
            ├─► Contract hashes account ID via Keccak-256
            ├─► Stores MuleAccount struct in mapping[bytes32]
            ├─► Emits AccountFlagged event
            ├─► Waits for tx receipt (timeout: 10s)
            │
            └─► Returns tx_hash to backend
                    │
                    └─► Backend logs tx_hash to DB
                        (Ingest still returns 200 OK)
```

### Verification Flow (Investigator)

```
Investigator views MuleRegistryPage
    │
    ├─► Queries GET /api/mule/registry
    ├─► Backend returns flagged accounts from DB + blockchain proof
    │
    ├─► Click account row → See blockchain details
    │   ├─► tx_hash
    │   ├─► block_number
    │   ├─► block_timestamp
    │   ├─► flagging_authority
    │   └─► evidence_basis
    │
    └─► (Optional) Query Ganache directly:
        geth console (if using Geth; Ganache doesn't expose console)
        → web3.eth.getTransactionReceipt('0xabc123...')
        → Verify AccountFlagged event was emitted
```

---

## Future Scope

The following features are conceptually designed but not yet implemented:

### Backend Enhancements
- **Refresh Token Rotation:** Implement separate refresh tokens with auto-rotation to mitigate token theft
- **2FA / MFA:** Add time-based one-time passwords (TOTP) for user login
- **Account Unflagging:** Implement `POST /api/mule/unflag` to reverse flagging if investigation is cleared
- **Bulk Complaint Import:** CSV/Excel upload for batch complaint ingestion
- **Advanced Filtering:** Full-text search on complaint descriptions and keywords
- **Batch Predictions:** Bulk prediction API for offline/batch scenarios

### ML/AI Enhancements
- **Online Learning:** Update model with new complaint data without full retraining
- **Ensemble Methods:** Combine XGBoost with other classifiers (LightGBM, CatBoost) for robustness
- **Anomaly Detection:** Unsupervised model to flag unusual complaint patterns
- **Network Analysis:** Graph-based mule network detection (identify connected accounts)
- **Time-Series Forecasting:** Predict high-risk time windows per ATM/district
- **Natural Language Processing:** Extract fraud patterns from complaint narratives

### Blockchain Enhancements
- **Multi-Signature Authorization:** Require multiple agencies to jointly flag high-risk accounts
- **Chain Migration:** Move from Ganache to production Ethereum testnet (Sepolia) or Layer 2 (Polygon)
- **Decentralized Oracle:** Integrate Chainlink oracle for off-chain data (e.g., real-time ATM availability)
- **Smart Contract Upgrades:** Implement proxy pattern for contract versioning without data loss

### Frontend Enhancements
- **User Preferences:** Save dashboard preferences (columns, filters, theme) to backend
- **Mobile App:** React Native version for iOS/Android
- **Advanced Visualizations:** 3D heatmaps, animated flow diagrams, network graphs
- **Offline Mode:** Service Worker caching for offline complaint review
- **Dark Mode:** Theme toggle with system preference detection

### Security Enhancements
- **SSL/TLS Enforcement:** Migrate from HTTP to HTTPS with certificate pinning
- **Encryption at Rest:** Database-level encryption for sensitive PII
- **Rate Limit Refinement:** Implement per-user rate limits (not just per-IP)
- **Secrets Management:** Use HashiCorp Vault or AWS Secrets Manager for credential rotation
- **Penetration Testing:** Third-party security audit before production deployment

### Operational
- **Deployment Automation:** Kubernetes/Docker containers for scalable deployment
- **Monitoring & Alerting:** Prometheus + Grafana for system health, Sentry for error tracking
- **Database Replication:** Master-slave PostgreSQL setup for high availability
- **API Versioning:** Implement API versioning (v1, v2) for backward compatibility
- **Documentation Generation:** Auto-generate OpenAPI specs from code; maintain API contracts

### Compliance & Governance
- **GDPR Compliance:** Right-to-be-forgotten (RTBF), data portability, consent management
- **Audit Report Generation:** Automated compliance reports for regulatory reviews
- **Role Expansion:** Add new roles (Regional Admin, State Admin) with hierarchical permissions
- **Data Retention Policy:** Automatic purging of old records per legal retention requirements

---

## Full Demo Flow

### Role 1 — Cyber Cell Officer
1. Login as `cyber_delhi` → Command Centre loads with LIVE indicator
2. Run ingest → alert appears in Command Centre in real-time (<1 second)
3. Alert card shows: complaint_id, tracking number, ATM ID, coordinates, freezable amount, dispatch status (Webhook SENT)
4. Click alert card → Alert Detail Page
5. See district, fraud type, risk score badge
6. Left panel: Linked Complaints (same district, same risk level, from DB)
7. Right panel: SHAP bar chart (real per-prediction TreeExplainer values)
8. Directional influence table: which features increase/decrease risk score
9. Click "Deploy Team" → action recorded
10. Click "Download Report" → HTML report opens: SHAP + dispatch + linked complaints + action taken
11. Navigate to Heatmap → choropleth map of 10 districts
12. Click Delhi zone → drill down to ranked ATMs with risk scores
13. Navigate to Dispatch Log → SENT records for all ingested complaints
14. Navigate to Mule Registry → flagged accounts with on-chain proof
15. Navigate to Blockchain Log → tx hashes from Ganache

### Role 2 — I4C Admin
1. Login as `i4c_admin` → I4C Admin Console
2. Stats: HIGH alerts, MEDIUM alerts, LOW alerts, total complaints, active zones
3. Command Centre → same real-time WebSocket feed
4. Heatmap → all districts visible
5. Blockchain Log → full audit trail
6. Mule Registry → all flagged accounts
7. Reports → District/Bank/Fraud-type breakdown with charts and CSV export

### Role 3 — Bank Nodal Officer
1. Login as `bank_sbi` → Bank Nodal Dashboard
2. Total Freezable Amount Today, Accounts Flagged, Pending Freeze Actions
3. Dispatch Log → bank-relevant alerts only
4. Reports → aggregate analytics, CSV download

---

## All API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | No | Get JWT token |
| POST | `/api/auth/logout` | Yes | Revoke token |
| POST | `/api/complaints/ingest` | Yes | Core pipeline |
| GET | `/api/dashboard/stats` | No | Aggregate stats |
| GET | `/api/alerts/recent?limit=N` | Yes | Recent HIGH/MEDIUM alerts |
| GET | `/api/alerts/detail/{id}` | Yes | Full alert detail + SHAP |
| GET | `/api/alerts/dispatch-log` | Yes | Dispatch status |
| GET | `/api/heatmap` | Yes | GIS risk zone data |
| GET | `/api/reports/by-district` | Yes | District aggregate |
| GET | `/api/reports/by-bank` | Yes | Bank aggregate |
| GET | `/api/reports/by-fraud-type` | Yes | Fraud type aggregate |
| GET | `/api/reports/export` | Yes | CSV export |
| GET | `/api/mule-accounts` | Yes | Mule registry |
| WS | `/ws/alerts` | No | Real-time alert feed |

---

## Integration Fixes (Post-Evaluation Session, Sep 2 2026)

| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| WebSocket double connection | `StrictMode` in `main.tsx` causes double mount | Removed `StrictMode` |
| Mock data on dashboard | `SocketContext.tsx` making second WS connection to port 3001 | Converted to dummy provider |
| Alert disappearing on refresh | Events only in memory, lost on reconnect | Created `/api/alerts/recent`; loads DB on WS connect |
| AlertsPage showing mock data | `import { alerts } from '@/mockData'` | Replaced with real API fetch |
| AlertDetailPage showing mock data | `getAlertById()` from mockData | Real fetch from `/api/alerts/detail/{id}` |
| Download Report broken | `generateCasePdf()` expected old `AlertItem` type | Updated to accept `any`, normalize real API fields |
| Alerts page district/fraudType empty | Mapping error: district set to complaint_id | Fixed mapping + updated `/api/alerts/recent` to return district, state, fraud_type, risk_score |

---

## Counter Answers for Judges

| Question | Answer |
|----------|--------|
| Why synthetic data? | Real I4C data legally restricted. NCRB typologies used. Production = authorized I4C OpenAPI feed via MoU |
| Why all HIGH risk? | 10 districts chosen are cybercrime-prone intentionally. National data gives natural distribution |
| SMS/Email PENDING? | MSG91/SMTP not wired in prototype. Webhook + Dashboard = SENT — check Dispatch Log |
| Why web dashboard? | PS requirement + engine is API that plugs into Pratibimb (MHA) |
| NCRP integration? | Same JSON format. Live feed starts after MoU with I4C |
| SHAP hardcoded? | Real TreeExplainer per prediction. Only feature name labels are mapped to human-readable strings |
| Blockchain = mule detection? | No — immutable cross-state LEA audit trail. ML does detection |
| Why Ganache? | Local Ethereum testnet. Production: Hyperledger Fabric (permissioned, government preferred) |
| Hops kaise pata? | Input field in complaint form — not predicted by model |
| Delayed complaint scenario? | Cash gone but mule flagged in registry + heatmap updated for future prevention |

---

## Branch Structure

```
main                ← Final merged (Aniket manages)
├── kanav           ← Security/JWT
├── saina-db        ← Database schema + ATM data
├── kartike         ← FastAPI backend
├── saina-ml        ← ML model
├── himanshu        ← React frontend
└── aniket          ← Blockchain
```

**Merge order:** `kanav → saina-db → kartike → saina-ml → himanshu → aniket → main`

---

## License

CyberSight is released under the **Apache License 2.0**.

See [LICENSE](LICENSE) for details.

---

## Acknowledgments

CyberSight is developed for the **Smart India Hackathon 2026** (Problem Statement PS 26184) under the **Ministry of Home Affairs (MHA)** and the **Indian Cybercrime Coordination Centre (I4C)**.

**Team Members & Contributions:**
- **Kartike** — Backend API, JWT/RBAC, complaint ingestion pipeline, WebSocket alerts, rate limiting
- **Saina** — ML model (XGBoost), database design, synthetic data generation, ATM data curation
- **Aniket** — Blockchain module (Solidity, Ganache, Web3.py integration), smart contract security
- **Himanshu** — Frontend (React, TypeScript, TailwindCSS), heatmap visualization, SHAP charting
- **Kanav** — Security engineering, authentication/authorization design, audit logging

---

## Contact & Support

For questions, issues, or contributions, please refer to the project's Git repository or contact the development team.

---

**Last Updated:** January 2026  
**Status:** Integrated (SIH 2026 Submission)  
**Version:** 1.0.0
