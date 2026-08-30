from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.complaint import IngestRequest
from app.routers.ingest import call_predict

router = APIRouter(tags=["predict"])


@router.post("/predict")
def predict(complaint_data: IngestRequest, db: Session = Depends(get_db)):
    prediction_data = call_predict(complaint_data, db)
    top_atms = prediction_data.get("top_5_atms") or []

    return {
        "predicted_locations": [
            {"lat": a["lat"], "lng": a["lon"], "atm_id": a["atm_id"], "bank_name": a["bank_name"]}
            for a in top_atms
        ],
        "predicted_district": prediction_data["predicted_district"],
        "risk_level": prediction_data["risk_level"],
        "confidence": prediction_data["confidence"],
        "novel_pattern": prediction_data["novel_pattern"],
        "recommended_action": prediction_data["recommended_action"],
        "withdrawal_window_minutes": prediction_data["withdrawal_window_minutes"],
        "freezable_amount": prediction_data["freezable_amount"],
        "shap_values": prediction_data["shap_values"],
        "model": "xgboost-v1",
        "message": "Live prediction from Rishika's model",
    }