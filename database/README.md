# Database — Saina (Day 1)

## What's Here

| File | Purpose |
|------|---------|
| `schema.sql` | Full PostgreSQL + PostGIS schema for CyberSight |
| `generate_data.py` | Synthetic complaint generator — 50,000 records, 4 cities |
| `insert_atms.py` | Real ATM data insert — Delhi (797 ATMs) |
| `insert_atms_ncr.py` | Real ATM data insert — Delhi NCR (869 ATMs) |
| `insert_atms_mumbai.py` | Real ATM data insert — Mumbai (300 ATMs) |
| `insert_atms_jamtara.py` | Real ATM data insert — Jamtara (300 ATMs) |

## Database Setup

**Requirements:** PostgreSQL 15+, PostGIS extension

```bash
psql -U postgres -c "CREATE DATABASE cybersight;"
psql -U postgres -d cybersight -f schema.sql
```

## Synthetic Data

50,000 complaint records with 4-city distribution:

| City | District | State | Weight |
|------|----------|-------|--------|
| Delhi | Delhi | Delhi | 40% |
| Delhi NCR | Delhi NCR | Haryana | 25% |
| Mumbai | Mumbai | Maharashtra | 25% |
| Jamtara | Jamtara | Jharkhand | 10% |

**Verified:**
- hop_count vs amount correlation: ~0.45 ✅
- Same-area withdrawal rate: ~6.5% ✅

## ATM Data

Real coordinates from OpenStreetMap (Overpass API).

| City | ATMs |
|------|------|
| Delhi | 797 |
| Delhi NCR | 869 |