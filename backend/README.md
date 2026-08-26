# CyberSight — Backend API

> FastAPI-powered REST backend for CyberSight (Smart India Hackathon 2025 – PS 77)

---

# Overview

The Backend API is a core component of **CyberSight**, a predictive analytics framework developed for **Smart India Hackathon 2025 (PS 77)** under the **Ministry of Home Affairs (MHA)** and the **Indian Cybercrime Coordination Centre (I4C)**.

This module handles complaint ingestion, keyword detection, ML prediction routing, alert dispatch, WebSocket broadcasting, heatmap generation, report generation, JWT authentication, token revocation, audit logging, PII masking, and SQL injection validation using **FastAPI**, **SQLAlchemy**, and **PostgreSQL with PostGIS**.

---

# Development Status

## Day 1 Integration: Complete ✅

### Implemented Features

- [x] FastAPI project setup and folder structure
- [x] GitHub repo and branch setup
- [x] PostgreSQL connection via SQLAlchemy
- [x] Saina DB schema integration (fraud_type, tracking_number, alert_level, PostGIS)
- [x] POST /complaint — basic complaint creation
- [x] GET /complaints — list complaints with filters (alert_level, fraud_type) + PII masked
- [x] GET /complaints/{complaint_id} — fetch single complaint
- [x] GET /api/complaints/{complaint_id}/full — full detail with prediction, recovery, mule (X-Admin-Confirm required)
- [x] POST /api/complaints/ingest — keyword detection, SQL validation, tracking number, real ML predict(), alert dispatch
- [x] POST /api/auth/login — JWT token, single admin role, 8hr expiry, audit logged
- [x] POST /api/auth/logout — token revocation via SHA256 hash
- [x] JWT revocation middleware — all protected routes checked
- [x] Audit log — login success/failure logged to audit_log table
- [x] PII masking — mobile_number + beneficiary_account masked on GET /complaints
- [x] SQL injection validation — complaint_text, district, state validated on ingest
- [x] X-Admin-Confirm header — GET /api/complaints/{id}/full protected
- [x] GET /api/heatmap — GeoJSON with ATM risk layer + victim cluster layer
- [x] GET /api/mule-accounts — mule account list with blockchain status
- [x] GET /api/reports/case/{complaint_id} — individual case report
- [x] GET /api/reports/daily — daily consolidated report
- [x] WebSocket /ws/alerts — live alert broadcast for MEDIUM/HIGH complaints
- [x] Alert dispatch logic — LOW = DB only, MEDIUM/HIGH = WebSocket + alert_dispatch_log
- [x] Keyword → fraud_type detection via keyword_fraud_map table
- [x] Tracking number auto-generation (CS-YYYY-XXXXX format via DB trigger)
- [x] **Real ML model wired — cybersight_model.pkl (Rishika) live in predict()** ✅
- [x] **Blockchain httpx integration — NON-BLOCKING flag call on HIGH alert (Aniket)** ✅
- [x] **CORS middleware — http://localhost:5173 allowed (for Himanshu frontend)** ✅
- [x] **SlowAPI rate limiting — login 5/15min, ingest 100/hr (Kanav)** ✅
- [x] **GET /api/dashboard/stats — real DB query, live numbers** ✅
- [x] **Admin user inserted — admin@cybersight.in / CyberSight@2025** ✅
- [x] GET /health — server health check
- [x] GET /health/db — database connection check
- [x] Swagger UI at /docs
- [x] Environment variable setup via dotenv

---

# Problem Statement

Cybercriminals route stolen funds through multiple mule accounts and withdraw cash across ATMs before police can act.

CyberSight addresses this by:

- Ingesting NCRP complaints in real time
- Detecting fraud keywords and mapping to fraud_type automatically
- Calling ML model to predict exact ATM where cash will be withdrawn
- Dispatching alerts to I4C, CyberCell, Bank, and PoliceSHO before withdrawal
- Exposing heatmap, reports, and case detail endpoints for analyst dashboard
- Securing all endpoints with JWT authentication and token revocation

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| ASGI Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | PostgreSQL 15+ |
| Spatial Extension | PostGIS |
| Schema Validation | Pydantic |
| WebSocket | FastAPI WebSocket |
| Auth (JWT) | python-jose + passlib |
| Rate Limiting | SlowAPI |
| Blockchain | httpx (non-blocking call to Aniket's API) |
| ML Model | XGBoost + joblib (Rishika's cybersight_model.pkl) |
| ML Libraries | pandas, numpy, shap |
| Environment | python-dotenv |
| Runtime | Python 3.10+ |

---

# Project Structure
backend/

│

├── requirements.txt

├── .env.example

├── .env                        # NEVER commit

├── .gitignore

│

└── app/

├── main.py                 # FastAPI entry — JWT middleware, routers, health, CORS

├── database.py             # PostgreSQL engine + session

├── rate_limit.py           # SlowAPI limiter (shared across routers)

│

├── models/

│   ├── init.py

│   ├── complaint.py        # All SQLAlchemy models

│   ├── predict.py          # Rishika's real ML predict() function

│   ├── cybersight_model.pkl # Trained XGBoost model

│   └── atm_locations.csv   # ATM data for ML prediction

│

├── schemas/

│   ├── init.py

│   └── complaint.py        # Pydantic schemas — request/response validation

│

└── routers/

├── init.py

├── complaints.py       # GET /complaints, GET /full

├── predict.py          # GET /predict

├── auth.py             # POST /api/auth/login + /logout (rate limited)

├── ingest.py           # POST /api/complaints/ingest (ML + blockchain + rate limited)

├── heatmap.py          # GET /api/heatmap

├── mule.py             # GET /api/mule-accounts

├── reports.py          # GET /api/reports/case + /daily

└── websocket.py        # WebSocket /ws/alerts
---

# Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Runtime |
| PostgreSQL | 15+ | Database |
| PostGIS | (with PostgreSQL) | Geometry columns |

---

# Installation

## Clone Repository

```bash
git clone https://github.com/kartike37/cybercrime-prediction-sih
cd cybercrime-prediction-sih/backend
```

## Create Virtual Environment

```bash
python -m venv venv
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Database Setup

### 1. Create database

```sql
CREATE DATABASE cybercrime_db;
```

### 2. Run schema

```bash
psql -U postgres -d cybercrime_db -f database/schema.sql
```

### 3. Insert dummy ATM data

```sql
INSERT INTO atm_locations (atm_id, bank_name, address, district, state, risk_score)
VALUES
('ATM-DUMMY-001', 'SBI', 'Connaught Place', 'New Delhi', 'Delhi', 0.75),
('ATM-DUMMY-002', 'HDFC', 'Karol Bagh', 'New Delhi', 'Delhi', 0.45),
('ATM-DUMMY-003', 'ICICI', 'Lajpat Nagar', 'New Delhi', 'Delhi', 0.85);
```

### 4. Insert admin user

```bash
# Generate bcrypt hash in Python (venv activated):
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
print(pwd_context.hash("CyberSight@2025"))
```

```sql
INSERT INTO users (username, password_hash, role)
VALUES ('admin@cybersight.in', '<generated_hash>', 'admin');
```

---

# Environment Configuration

```bash
copy .env.example .env
```

Edit `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5433/cybercrime_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
GANACHE_URL=http://127.0.0.1:7545
```

---

# Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

---

# Authentication

**Admin credentials:**
- Username: `admin@cybersight.in`
- Password: `CyberSight@2025`

**Login:**
```json
POST /api/auth/login
{
  "username": "admin@cybersight.in",
  "password": "CyberSight@2025"
}
```

**All protected routes need:**
---

# API Endpoints

## Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Login — rate limited 5/15min |
| POST | `/api/auth/logout` | Logout — token revoked |

## Complaints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/complaints` | List — PII masked, filters: alert_level, fraud_type |
| GET | `/api/complaints/{id}/full` | Full detail — X-Admin-Confirm: true required |
| POST | `/api/complaints/ingest` | Full ingest — ML predict, blockchain flag, rate limited 100/hr |

## Dashboard & Heatmap
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard/stats` | Live stats — high/medium/low counts, weekly trend |
| GET | `/api/heatmap` | GeoJSON — ATM risk + victim clusters |

## Mule Accounts
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/mule-accounts` | All mule accounts with blockchain_tx_hash |

## Reports
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/reports/case/{complaint_id}` | Individual case report |
| GET | `/api/reports/daily` | Daily consolidated report |

## WebSocket
| Path | Description |
|------|-------------|
| `ws://localhost:8000/ws/alerts` | Live MEDIUM/HIGH alert broadcast |

## Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server health |
| GET | `/health/db` | DB connection |

---

# ML Integration

**Model:** `backend/app/models/cybersight_model.pkl` (XGBoost, trained by Rishika)

**Predict function:** `backend/app/models/predict.py`

**Input fields used:**
- district, victim_lat, victim_lon, beneficiary_lat, beneficiary_lon
- fraud_amount, already_withdrawn, number_of_hops
- hour, dow, month, is_weekend (calculated from transaction_timestamp)
- complaints_6h, complaints_24h (real DB query)
- district_risk_score (default 0.5)

**Output:** predicted_atm_id, predicted_atm_lat/lon, risk_level, fraud_probability, shap_values, freezable_amount, recommended_action, withdrawal_risk_window

---

# Integration Status

| Feature | Status | Owner |
|---------|--------|-------|
| FastAPI + PostgreSQL | ✅ Done | Kartike |
| All complaint endpoints | ✅ Done | Kartike |
| JWT auth + revocation | ✅ Done | Kartike + Kanav |
| Rate limiting (login + ingest) | ✅ Done | Kartike + Kanav |
| CORS for frontend | ✅ Done | Kartike |
| Real ML model (predict()) | ✅ Done | Kartike + Rishika |
| Blockchain httpx flag call | ✅ Done | Kartike + Aniket |
| Dashboard stats endpoint | ✅ Done | Kartike |
| WebSocket live alerts | ✅ Done | Kartike |
| Admin user setup | ✅ Done | Kartike + Saina |
| Frontend live wiring | 🔄 In Progress | Himanshu |
| Rishika laptop setup | ⏳ Day 3 | Rishika + Saina |

---

# Team

| Name | Role |
|------|------|
| Rishika Garg | ML / Data Engineer |
| Himanshu Jain | Full Stack Developer |
| Aniket Dixit | Blockchain Developer |
| Kartike Rohila | Backend Developer |
| Saina Sharma | Database Engineer |
| Kanav Agarwal | Security & Compliance Engineer |

---

**Status:** Day 1 Integration Complete ✅  
**Next:** Day 2 — Himanshu frontend live wiring | Day 3 — End-to-end test + demo dry run