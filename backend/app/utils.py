import secrets
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.complaint import Complaint


def generate_tracking_number(db: Session) -> str:
    """
    Generates a unique tracking number: CS + YYYYMMDD + 6-char hex.
    Retries on the rare collision instead of trusting randomness blindly.
    """
    for _ in range(5):
        candidate = f"CS{datetime.utcnow().strftime('%Y%m%d')}{secrets.token_hex(3).upper()}"
        exists = db.query(Complaint).filter(
            Complaint.tracking_number == candidate
        ).first()
        if not exists:
            return candidate
    # Extremely unlikely with 16M+ combinations/day, but fail loudly
    # rather than silently return a duplicate.
    raise RuntimeError("Could not generate a unique tracking_number after 5 attempts")


def find_nearest_atm(predicted_lat: float, predicted_lon: float, db: Session):
    """
    atm_locations.location is a PostGIS geometry column that is NOT
    ORM-mapped (models/complaint.py notes geoalchemy2 isn't installed),
    so this uses raw SQL. The <-> operator is PostGIS's index-backed
    nearest-neighbor distance operator.

    Returns a dict with atm_id, bank_name, district, lat, lon — or
    None if atm_locations is empty.
    """
    result = db.execute(
        text("""
            SELECT atm_id, bank_name, district,
                   ST_Y(location) AS lat, ST_X(location) AS lon
            FROM atm_locations
            ORDER BY location <-> ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
            LIMIT 1
        """),
        {"lat": predicted_lat, "lon": predicted_lon}
    ).fetchone()

    if result is None:
        return None

    return {
        "atm_id": result.atm_id,
        "bank_name": result.bank_name,
        "district": result.district,
        "lat": result.lat,
        "lon": result.lon,
    }