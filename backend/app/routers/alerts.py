from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import get_db
from app.models.complaint import Complaint, Prediction, MuleAccount

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/recent")
def get_recent_alerts(limit: int = 20, db: Session = Depends(get_db)):
    results = (
        db.query(Complaint, Prediction)
        .join(Prediction, Prediction.complaint_id == Complaint.complaint_id)
        .filter(Complaint.alert_level.in_(["HIGH", "MEDIUM"]))
        .order_by(desc(Complaint.complaint_datetime))
        .limit(limit)
        .all()
    )

    alerts = []
    for complaint, prediction in results:
        alerts.append({
            "complaint_id": complaint.complaint_id,
            "tracking_number": complaint.tracking_number,
            "alert_level": complaint.alert_level,
            "district": complaint.victim_district or "",
            "state": complaint.victim_state or "",
            "fraud_type": complaint.fraud_type or "",
            "risk_score": int((prediction.confidence_score or 0.8) * 100),
            "atm_id": prediction.predicted_atm_id,
            "atm_lat": float(prediction.predicted_lat) if prediction.predicted_lat else None,
            "atm_lon": float(prediction.predicted_lon) if prediction.predicted_lon else None,
            "recommended_action": prediction.recommended_action,
            "freezable_amount": float(prediction.freezable_amount) if prediction.freezable_amount else None,
            "timestamp": str(complaint.complaint_datetime),
            "dispatch_status": {
                "sms": "pending",
                "email": "pending",
                "webhook": "sent",
                "dashboard": "sent"
            }
        })

    return {"alerts": alerts, "total": len(alerts)}


@router.get("/detail/{complaint_id}")
def get_alert_detail(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    prediction = db.query(Prediction).filter(
        Prediction.complaint_id == complaint_id
    ).first()

    linked = db.query(Complaint).filter(
        Complaint.victim_district == complaint.victim_district,
        Complaint.alert_level == complaint.alert_level,
        Complaint.complaint_id != complaint_id
    ).order_by(desc(Complaint.complaint_datetime)).limit(4).all()

    linked_list = [
        {
            "id": c.complaint_id,
            "fraudType": c.fraud_type or "Unknown",
            "reporter": f"Victim {c.complaint_id[-3:]}",
            "amount": float(c.amount_lost or 0),
            "timestamp": str(c.complaint_datetime),
        }
        for c in linked
    ]

    mule_count = db.query(func.count(MuleAccount.id)).filter(
        MuleAccount.account_number == complaint.beneficiary_account
    ).scalar() or 0

    return {
        "id": complaint.complaint_id,
        "district": complaint.victim_district or "",
        "state": complaint.victim_state or "",
        "fraudType": complaint.fraud_type or "Unknown",
        "riskLevel": complaint.alert_level or "HIGH",
        "riskScore": int((prediction.confidence_score or 0.8) * 100) if prediction else 80,
        "predictedWithdrawalWindow": "Next 4 hours",
        "linkedComplaints": linked_list,
        "muleAccounts": mule_count,
        "recommendedAction": prediction.recommended_action if prediction else "",
        "shapValues": prediction.shap_values if prediction else {},
        "freezableAmount": float(prediction.freezable_amount or 0) if prediction else 0,
        "atmId": prediction.predicted_atm_id if prediction else "",
    }