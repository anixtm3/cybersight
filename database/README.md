# CyberSight — Database (Saina)

**Branch:** `saina`  
**Stack:** PostgreSQL 15 + PostGIS 3.6.2, port 5433, database: `cybersight`

---

## What I Built

### 1. Schema (`database/schema.sql`)

**Tables:**

| Table | Purpose |
|-------|---------|
| `users` | Auth — 3 roles, jurisdiction scoping, bank scoping |
| `complaints` | Core complaint records — 28 ML features populated |
| `atm_locations` | 4,625 real ATMs with PostGIS geometry |
| `predictions` | ML output — Top 5 ATMs, SHAP, confidence, risk level |
| `dispatch_log` | 4-channel alert delivery records |
| `mule_accounts` | Flagged beneficiary accounts |
| `case_notes` | Investigator notes per complaint |
| `action_log` | Officer actions per complaint — includes `details TEXT` for CCTV notes |
| `audit_log` | System-wide sensitive action audit trail |
| `keyword_fraud_map` | Keyword → fraud type mapping |
| `registry_provenance` | Blockchain provenance — columns: `id, created_at, account_hash, tx_hash, flagging_authority, flag_basis` |

**Key schema decisions:**

- `users.jurisdiction_district` — enforces district-scoped data access for `cyber_cell_officer`
- `users.bank_name` — enforces bank-scoped access for `bank_nodal_officer`
- 3-role CHECK constraint: `cyber_cell_officer`, `bank_nodal_officer`, `admin`
- `complaints.tracking_number` — format `CS-2026-XXXXXXX` (7 digits, LPAD)
- `atm_locations.location` — PostGIS `GEOGRAPHY(POINT, 4326)` with GIST index for fast radius queries
- `audit_log.log_id` — no `server_default`, must be supplied explicitly on insert

### 2. ATM Data (`database/atm_inserts/`)

Real ATM coordinates sourced via Overpass Turbo (OpenStreetMap):

| District | ATMs |
|----------|------|
| Bengaluru | 1,137 |
| Delhi NCR | 869 |
| Delhi | 797 |
| Hyderabad | 566 |
| Pune | 457 |
| Mumbai | 300 |
| Jamtara | 300 (synthetic — correct bounding box 23.8–24.2°N, 86.8–87.2°E) |
| Patna | 89 |
| Lucknow | 57 |
| Agra | 53 |
| **Total** | **4,625** |

### 3. Synthetic Data (`ML/generate_data.py`)

419,863 complaint rows — all 28 ML features populated, `target_atm_id` nulls: 0.

**Key fixes applied during generation:**
- `np.float64` cast to `float()` before PostGIS queries — prevents silent failures
- `conn.autocommit = True` — prevents rollback on large batches
- Tracking number sequence: LPAD 7 digits, restarted at 100001 for second run
- Split into two runs: 99,999 rows + 400,001 rows (`start_index=100000`)
- ANOVA fix: removed hardcoded `preferred_bearing` from `BANK_CONFIG` — replaced with randomized logic (was creating artificial ML signal, p ~10⁻⁷⁵)

---

## Verified

- Schema runs cleanly on fresh DB — zero errors ✅
- PostGIS 5km radius query — returns correct ATM counts ✅
- Foreign key integrity — enforced ✅
- 419,863 complaints — `target_atm_id` nulls: 0 ✅
- All 28 ML features populated ✅
- 10 districts, 4,625 ATMs ✅

---

## Setup

```bash
# Create DB
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE cybersight;"

# Enable extensions
psql -h localhost -p 5433 -U postgres -d cybersight -c "CREATE EXTENSION postgis; CREATE EXTENSION pgcrypto;"

# Run schema
psql -h localhost -p 5433 -U postgres -d cybersight -f database/schema.sql

# Insert ATM data
psql -h localhost -p 5433 -U postgres -d cybersight -f database/atm_inserts/all_cities.sql
```

**Demo users** — insert once:
```sql
INSERT INTO users (username, password_hash, role, jurisdiction_district, bank_name) VALUES
('cyber_delhi', '<bcrypt hash>', 'cyber_cell_officer', 'Delhi', NULL),
('i4c_admin',  '<bcrypt hash>', 'admin', NULL, NULL),
('bank_sbi',   '<bcrypt hash>', 'bank_nodal_officer', NULL, 'SBI');
```