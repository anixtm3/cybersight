from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api", tags=["heatmap"])


@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):

    # Layer 1 — ATM risk points (PostGIS geometry se lat/lon)
    atm_query = text("""
        SELECT 
            atm_id,
            bank_name,
            district,
            state,
            risk_score,
            ST_Y(location::geometry) as lat,
            ST_X(location::geometry) as lon
        FROM atm_locations
        WHERE location IS NOT NULL
    """)
    atms = db.execute(atm_query).fetchall()

    atm_features = []
    for atm in atms:
        atm_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [atm.lon, atm.lat]
            },
            "properties": {
                "layer": "atm",
                "atm_id": atm.atm_id,
                "bank_name": atm.bank_name,
                "risk_score": float(atm.risk_score) if atm.risk_score else 0,
                "district": atm.district,
                "state": atm.state
            }
        })

    # Layer 2 — Victim cluster points
    victim_query = text("""
        SELECT 
            complaint_id,
            tracking_number,
            fraud_type,
            alert_level,
            victim_lat,
            victim_lon
        FROM complaints
        WHERE victim_lat IS NOT NULL
        AND victim_lon IS NOT NULL
    """)
    complaints = db.execute(victim_query).fetchall()

    victim_features = []
    for c in complaints:
        victim_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [c.victim_lon, c.victim_lat]
            },
            "properties": {
                "layer": "victim",
                "complaint_id": c.complaint_id,
                "tracking_number": c.tracking_number,
                "fraud_type": c.fraud_type,
                "alert_level": c.alert_level
            }
        })

    return {
        "type": "FeatureCollection",
        "layers": {
            "atm_risk": len(atm_features),
            "victim_cluster": len(victim_features)
        },
        "features": atm_features + victim_features
    }