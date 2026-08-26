from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.complaint import IngestRequest
from app.routers.ingest import call_predict

router = APIRouter(tags=["predict"])


# ✅ FIX (Day 2 task): this route used to return hardcoded dummy data
# ("dummy-v0" / "ML integration pending — Rishika"). It now calls the
# real model through ingest.py's call_predict() helper — the same
# function /api/complaints/ingest already uses — so both endpoints
# stay in sync and there's no duplicated prediction logic.
#
# Changed GET -> POST because the real model needs input data
# (district, lat/lon, amount, etc.) which a GET with no body can't
# carry. Reuses the existing IngestRequest schema — no new schema
# needed. This endpoint does NOT save anything to the database; it
# only returns a prediction, for quick testing/demo purposes.
@router.post("/predict")
def predict(complaint_data: IngestRequest, db: Session = Depends(get_db)):
    prediction_data = call_predict(complaint_data, db)

    return {
        "predicted_locations": [
            {
                "lat": prediction_data["predicted_atm_lat"],
                "lng": prediction_data["predicted_atm_lon"],
                "confidence": prediction_data["fraud_probability"],
                "label": prediction_data["predicted_atm_id"],
            }
        ],
        "risk_level": prediction_data["risk_level"],
        "recommended_action": prediction_data["recommended_action"],
        "withdrawal_risk_window": prediction_data["withdrawal_risk_window"],
        "freezable_amount": prediction_data["freezable_amount"],
        "model": "xgboost-v1",
        "message": "Live prediction from Rishika's model",
    }