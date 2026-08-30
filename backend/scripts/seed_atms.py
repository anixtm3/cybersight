
"""
scripts/seed_atms.py

Loads the REAL ATM dataset (500 ATMs across 10 cities) from
app/models/atm_locations.csv into the atm_locations table.

Run from the backend/ directory (where app/ is a sibling):
    python -m scripts.seed_atms

CONFIRMED against live DB: atm_locations columns are
(id, location, risk_score, address, district, state, atm_id, bank_name).

⚠️ GAP: the CSV has historical_fraud_count and atm_fraud_rate_last_30days,
but atm_locations has no matching columns for either. Only a derived
risk_score (0-100, scaled from atm_fraud_rate_last_30days) is stored here.
If Rishika's feature engineering needs the raw historical_fraud_count or
the exact fraud rate, read them directly from this CSV — they are not
recoverable from the DB after this seed runs. If the team wants them
queryable via the API too, that needs an additive migration first
(ALTER TABLE atm_locations ADD COLUMN historical_fraud_count INTEGER,
ADD COLUMN atm_fraud_rate_last_30days NUMERIC(5,4)) — ask Saina before
adding it, since it's her schema.

There's no separate street-level address in the source data, so
`address` is built as "{district}, {state}" rather than fabricated.
"""

import csv
from pathlib import Path

from sqlalchemy import text
from app.database import SessionLocal

CSV_PATH = Path(__file__).resolve().parent.parent / "app" / "models" / "atm_locations.csv"


def compute_risk_score(fraud_rate_30d: float) -> int:
    """Scales the 0.0-1.0 fraud-rate fraction to a 0-100 risk_score."""
    return round(min(max(fraud_rate_30d, 0.0), 1.0) * 100)


def seed():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"ATM CSV not found at {CSV_PATH}")

    db = SessionLocal()
    count = 0
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                risk_score = compute_risk_score(float(row["atm_fraud_rate_last_30days"]))
                address = f"{row['district']}, {row['state']}"

                db.execute(
                    text("""
                        INSERT INTO atm_locations (atm_id, bank_name, location, district, state, address, risk_score)
                        VALUES (
                            :atm_id, :bank_name,
                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geometry,
                            :district, :state, :address, :risk_score
                        )
                        ON CONFLICT (atm_id) DO NOTHING
                    """),
                    {
                        "atm_id": row["atm_id"],
                        "bank_name": row["bank_name"],
                        "lat": float(row["lat"]),
                        "lon": float(row["lon"]),
                        "district": row["district"],
                        "state": row["state"],
                        "address": address,
                        "risk_score": risk_score,
                    },
                )
                count += 1
        db.commit()
        print(f"Seeded {count} ATM locations from {CSV_PATH.name} (existing atm_ids skipped).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()