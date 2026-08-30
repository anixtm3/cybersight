# CyberSight — Backend (Kartike)

**Branch:** `kartike`  
**Stack:** FastAPI (Python 3.11), PostgreSQL 15 + PostGIS, XGBoost, SQLAlchemy, SlowAPI

---

## What I Built

### 1. Auth & RBAC (`app/routers/auth.py`, `app/auth_core.py`)
- JWT login endpoint — `/api/auth/login`
- Three roles enforced: `cyber_cell_officer`, `bank_nodal_officer`, `admin`
- Jurisdiction scoping — cyber cell officers can only see complaints from their own district
- Token revocation check on every request via middleware
- Rate limiting — 429 after 5 rapid failed login attempts

### 2. Complaint Ingest Pipeline (`app/routers/ingest.py`)
- `POST /api/complaints/ingest` — full end-to-end pipeline:
  - Input validation (null bytes, length limits)
  - Keyword-based fraud type detection
  - Duplicate complaint ID check
  - Complaint saved to DB
  - 6 real-time features computed (rolling 6h count, district risk score, ATM density via PostGIS, time since last complaint same bank, mule flag, festival period)
  - XGBoost prediction called → Top 5 ATMs returned
  - Prediction record saved with SHAP values, confidence, freezable amount
  - Dispatch log written for MEDIUM/HIGH alerts
  - Blockchain flag triggered for HIGH alerts (non-blocking, timeout-bounded)
  - WebSocket broadcast for MEDIUM/HIGH alerts
  - Failure paths hardened — orphan rows marked `prediction_failed`, no raw tracebacks exposed to client

### 3. ML Integration (`app/models/predict.py`)
- Loads `ML/model.pkl` (XGBoost + encoders + ATM dataframe) once at startup
- 19-feature input contract — exact order matches training
- Confidence threshold gate — `< 0.4` → `ANALYST_REVIEW` suppresses auto-dispatch
- SHAP values computed per prediction via `TreeExplainer`
- Top 5 ATMs ranked from `atm_df` by predicted district
- Freezable amount = `amount_lost * 0.6`
- Safe encoder fallback — unseen labels return `0` instead of crashing

### 4. Blockchain Integration (`app/routers/ingest.py`)
- `flag_mule_on_blockchain()` — non-blocking POST to Aniket's service at `localhost:8001`
- Hashing handled server-side by Aniket's Solidity contract (Keccak-256)
- Graceful degrade — if Ganache is down, ingest still returns 200

### 5. WebSocket Alerts (`app/routers/websocket.py`)
- `/ws/alerts` — live broadcast to connected clients
- Broadcast triggered on every MEDIUM/HIGH ingest
- Payload fields match Himanshu's frontend contract exactly

### 6. Evidence Module (`app/routers/evidence.py`)
- `POST /api/complaints/{id}/notes` — case notes
- `POST /api/complaints/{id}/actions` — action log
- `GET` endpoints for both
- Officer ID pulled from JWT, never from client

### 7. Reports & Export (`app/routers/reports.py`)
- District-wise, bank-wise, fraud-typology-wise aggregates
- CSV export — `?format=csv`

### 8. Heatmap Endpoint (`app/routers/heatmap.py`)
- GeoJSON response with filterable parameters — date range, district, fraud type, risk level

---

## Verified End-to-End

- Login → JWT token ✅
- Jurisdiction scoping — officer sees only own district complaints ✅
- Ingest → prediction → DB write → `TEST-LIVE-003` → `200 OK` ✅
- `alert_level: HIGH`, `predicted_atm_id: DEL00001` ✅
- Failure path — prediction fail → `complaint.status = prediction_failed` ✅
- Model unavailable → generic 503, no traceback ✅
- WebSocket broadcast — confirmed via manual test ✅
- Blockchain down → ingest still returns 200 ✅
- Latency — steady state 192–240ms ✅

---

## Pending / In Progress

- Kanav's `alert_dispatch.py` + `ws_auth.py` — PR received, merge pending
- WebSocket JWT auth tests — not yet run post-merge
- Admin + Bank Nodal login — not yet tested end-to-end
- OpenAPI docs — complaints/ingest done, heatmap/reports/mule/evidence TBD
- Startup script — single command to bring up full stack

---

## Setup

**Requirements:** Python 3.11, PostgreSQL 15 + PostGIS on port 5433, `ML/model.pkl` at repo root

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create `backend/.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5433/cybersight
SECRET_KEY=cybersight-secret-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GANACHE_URL=http://127.0.0.1:7545
ACCOUNT_HASH_SALT=9957724d3e3a4deb71e3b9abae516163d431d72a040e0345bc493a166add44f4
```

```bash
uvicorn app.main:app --reload --port 8000
```

**Demo users** (insert once into DB):
```sql
INSERT INTO users (username, password_hash, role, jurisdiction_district, bank_name) VALUES
('cyber_delhi', '<bcrypt hash of password123>', 'cyber_cell_officer', 'Delhi', NULL),
('i4c_admin',  '<bcrypt hash of password123>', 'admin', NULL, NULL),
('bank_sbi',   '<bcrypt hash of password123>', 'bank_nodal_officer', NULL, 'SBI');
```

**ML model:** Place `model.pkl` from `saina-ml` branch at `ML/model.pkl` (repo root level, outside `backend/`).

---

## Key Decisions

| Decision | Reason |
|----------|--------|
| `atm_density` uses victim coords at inference | Withdrawal coords are the prediction target — circular dependency |
| `is_festival_period` hardcoded to 0 | Festival dates in model are 2024-only; demo is 2026 |
| `account_age_days` defaults to 180 | Not available at complaint time |
| Confidence < 0.4 → ANALYST_REVIEW | Suppress auto-dispatch on uncertain predictions |
| Blockchain flag non-blocking | Ingest latency must stay under 60s regardless of chain state |
