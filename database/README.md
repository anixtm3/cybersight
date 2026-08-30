
**Port:** 5433 (non-default — update all connection strings accordingly)

---

## Setup Steps

### 1. Create Database
```sql
CREATE DATABASE cybersight;
\c cybersight
CREATE EXTENSION postgis;
CREATE EXTENSION pgcrypto;
```

### 2. Run Schema
```sql
\i database/schema.sql
```

### 3. Insert ATM Data (run in this order)
```bash
python database/insert_atms.py
python database/insert_atms_ncr.py
python database/insert_atms_mumbai.py
python database/insert_jamtara_atms.py
python database/insert_atms_bengaluru.py
python database/insert_atms_hyderabad.py
python database/insert_atms_agra.py
python database/insert_atms_patna.py
python database/insert_atms_pune.py
python database/insert_atms_lucknow.py
```

### 4. Generate Synthetic Complaints
```bash
python database/generate_data.py
```

---

## ATM Coverage — 10 Districts

| District | State | ATMs | Source |
|----------|-------|------|--------|
| Bengaluru | Karnataka | 1,137 | OSM/Overpass |
| Delhi NCR | Haryana | 869 | OSM/Overpass |
| Delhi | Delhi | 797 | OSM/Overpass |
| Hyderabad | Telangana | 566 | OSM/Overpass |
| Pune | Maharashtra | 457 | OSM/Overpass |
| Mumbai | Maharashtra | 300 | OSM/Overpass |
| Jamtara | Jharkhand | 300 | Synthetic* |
| Patna | Bihar | 89 | OSM/Overpass |
| Lucknow | Uttar Pradesh | 57 | OSM/Overpass |
| Agra | Uttar Pradesh | 53 | OSM/Overpass |
| **Total** | | **4,625** | |

*Jamtara: OSM data unavailable. Synthetic coordinates within correct bounding box (23.8–24.2°N, 86.8–87.2°E).

---

## Synthetic Dataset

| Stat | Value |
|------|-------|
| Total rows | ~419,863 |
| Year | 2024 |
| Districts | 10 |
| Unique target ATMs | 2,593 |
| Insider cases | 5% |
| Festival period rows | ~27,000 |

### ML Features Generated

| Feature | Description |
|---------|-------------|
| `fraud_type` | 8 types (UPI, OLX, Investment, Romance, KYC, Job, Lottery, Tech Support) |
| `amount_lost` | Log-normal per fraud type |
| `number_of_hops` | Correlated with amount |
| `victim_lat/lon` | Within district bounding box |
| `withdrawal_lat/lon` | Displaced by fraud pattern |
| `target_atm_id` | PostGIS nearest ATM to withdrawal point |
| `is_festival_period` | 20 Indian festivals 2024 |
| `hour_of_day_sin/cos` | Cyclical time encoding |
| `day_of_week` | 0=Monday to 6=Sunday |
| `is_weekend` | Boolean |
| `account_age_days` | Correlated with fraud type |
| `mule_network_flag` | Probability increases with hop count |
| `rolling_6h_complaint_count` | Same district, last 6 hours |
| `district_risk_score` | Normalized complaint density per district |
| `atm_density` | ATMs within 5km of withdrawal point |
| `time_since_last_complaint_same_bank` | Hours since last same-bank complaint |
| `victim_to_withdrawal_distance_km` | Euclidean displacement |
| `is_insider_case` | 5% cases, withdrawal 2-5km from victim |

**Data statement:** Synthetic dataset designed from NCRB/I4C published fraud typologies. No real PII or case data. Production deployment requires retraining on authorised I4C data under MoU.

---

## Schema — Key Tables

| Table | Purpose |
|-------|---------|
| `complaints` | Core complaint data + all ML features |
| `atm_locations` | 4,625 ATMs with PostGIS geometry |
| `predictions` | Model output per complaint |
| `alerts` | Alert records |
| `alert_dispatch_log` | Multi-channel dispatch audit |
| `users` | 3-role RBAC |
| `mule_accounts` | Mule account registry |
| `registry_provenance` | Blockchain evidence |
| `case_notes` | Investigator evidence documentation |
| `action_log` | Officer action tracking |
| `dispatch_log` | Alert channel log |
| `revoked_tokens` | JWT revocation |
| `audit_log` | Admin audit trail |

---

## Key Schema Details

### Roles
```sql
CHECK (role IN ('admin', 'cyber_cell_officer', 'bank_nodal_officer'))
```

### Tracking Number Format
`CS-2026-XXXXXXX` — 7 digits, auto-generated via trigger on INSERT.

### JWT vs DB Field
- JWT payload: `jurisdiction`
- DB column: `jurisdiction_district`
- Intentionally different — do not change either.

---

## Integration Notes

| Item | Detail |
|------|--------|
| Port | 5433 (not default 5432) |
| PostGIS | Required — `ST_DWithin`, `<->` operator used |
| np.float64 | Always cast to `float()` before PostGIS queries |
| district_risk_score | Pre-computed in complaints table — fetch via AVG per district |
| atm_density | Compute real-time via PostGIS 5km radius query |
| time_since_last_complaint_same_bank | Compute real-time from complaints table, default -1 if none |
| account_age_days | Default 180 for demo |
| mule_network_flag | Derive: 1 if number_of_hops >= 4, else 0 |

---

## ML Model

See `ML/` branch (`saina-ml`) for training code and model.pkl.

- **Approach:** XGBoost district classifier → PostGIS Top 5 ATM ranking
- **Top-1 Accuracy:** 90%
- **Top-5 Accuracy:** 100%