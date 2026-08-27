import csv
import io
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint, Prediction, MoneyRecoveryStatus

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _to_csv(rows: list[dict]) -> StreamingResponse:
    if not rows:
        rows = [{}]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=report.csv"},
    )


# ─── GET /api/reports/case/{complaint_id} ────────────────
@router.get("/case/{complaint_id}")
def get_case_report(complaint_id: str, db: Session = Depends(get_db)):

    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    prediction = db.query(Prediction).filter(
        Prediction.complaint_id == complaint_id
    ).order_by(Prediction.predicted_at.desc()).first()

    # FIX: was complaint.id (int PK) — MoneyRecoveryStatus.complaint_id is the
    # string business ID (matches complaints.complaint_id), not the PK.
    recovery = db.query(MoneyRecoveryStatus).filter(
        MoneyRecoveryStatus.complaint_id == complaint.complaint_id
    ).first()

    return {
        "report_type": "individual_case",
        "generated_at": str(datetime.utcnow()),
        "complaint_id": complaint.complaint_id,
        "tracking_number": complaint.tracking_number,
        "fraud_type": complaint.fraud_type,
        "alert_level": complaint.alert_level,
        "victim_district": complaint.victim_district,
        "victim_state": complaint.victim_state,
        "amount_lost": float(complaint.amount_lost) if complaint.amount_lost else None,
        "prediction": {
            "predicted_atm_id": prediction.predicted_atm_id if prediction else None,
            "predicted_lat": prediction.predicted_lat if prediction else None,
            "predicted_lon": prediction.predicted_lon if prediction else None,
            "risk_level": prediction.risk_level if prediction else None,
            "recommended_action": prediction.recommended_action if prediction else None,
            "withdrawal_risk_window": prediction.withdrawal_risk_window if prediction else None,
            "freezable_amount": float(prediction.freezable_amount) if prediction and prediction.freezable_amount else None,
        } if prediction else None,
        "money_recovery": {
            # FIX: column names now match the real model
            # (amount_lost / amount_withdrawn / amount_recoverable / recovery_status)
            "amount_lost": float(recovery.amount_lost) if recovery and recovery.amount_lost else None,
            "amount_withdrawn": float(recovery.amount_withdrawn) if recovery and recovery.amount_withdrawn else None,
            "amount_recoverable": float(recovery.amount_recoverable) if recovery and recovery.amount_recoverable else None,
            "recovery_status": recovery.recovery_status if recovery else None,
        } if recovery else None,
        "software_contribution": {
            "what_detected": f"Fraud keywords detected: {complaint.fraud_keywords}",
            "what_predicted": f"ATM {prediction.predicted_atm_id} at ({prediction.predicted_lat}, {prediction.predicted_lon})" if prediction else "Prediction pending",
            "accounts_flagged": complaint.beneficiary_account or "None",
            "atm_locations_predicted": prediction.predicted_atm_id if prediction else "None",
            "money_potentially_saved": float(prediction.freezable_amount) if prediction and prediction.freezable_amount else 0,
            "actions_recommended": prediction.recommended_action if prediction else "None",
        }
    }


# ─── GET /api/reports/daily ──────────────────────────────
@router.get("/daily")
def get_daily_report(db: Session = Depends(get_db)):

    today = date.today()

    total_cases = db.query(Complaint).filter(
        func.date(Complaint.created_at) == today
    ).count()

    high_count = db.query(Complaint).filter(
        Complaint.alert_level == 'HIGH',
        func.date(Complaint.created_at) == today
    ).count()
    medium_count = db.query(Complaint).filter(
        Complaint.alert_level == 'MEDIUM',
        func.date(Complaint.created_at) == today
    ).count()
    low_count = db.query(Complaint).filter(
        Complaint.alert_level == 'LOW',
        func.date(Complaint.created_at) == today
    ).count()

    fraud_trends = db.query(
        Complaint.fraud_type,
        func.count(Complaint.id).label('count')
    ).filter(
        func.date(Complaint.created_at) == today
    ).group_by(Complaint.fraud_type).all()

    total_amount = db.query(
        func.sum(Complaint.amount_lost)
    ).filter(
        func.date(Complaint.created_at) == today
    ).scalar()

    predictions_today = db.query(Prediction).filter(
        func.date(Prediction.predicted_at) == today
    ).count()

    return {
        "report_type": "daily_consolidated",
        "date": str(today),
        "generated_at": str(datetime.utcnow()),
        "total_cases": total_cases,
        "alert_distribution": {"HIGH": high_count, "MEDIUM": medium_count, "LOW": low_count},
        "fraud_trends": [{"fraud_type": ft, "count": c} for ft, c in fraud_trends],
        "recovery_statistics": {
            "total_amount_lost": float(total_amount) if total_amount else 0,
            "cases_with_recovery": 0,
            "total_recovered": 0,
        },
        "model_performance_metrics": {
            # NOTE: still no real accuracy figure — Rishika hasn't shipped
            # metrics yet. Leaving this explicitly null rather than a
            # hardcoded percentage that nobody actually computed. Replace
            # once her metrics pack (Day 2 deliverable) lands.
            "model_version": "xgboost-v1",
            "accuracy": None,
            "accuracy_note": "pending validated metrics from Rishika — do not report a number here until then",
            "predictions_today": predictions_today,
        },
        "software_contribution_summary": {
            "total_atms_predicted": predictions_today,
            "high_risk_intercepted": high_count,
            "total_freezable_amount": float(
                db.query(func.sum(Prediction.freezable_amount)).filter(
                    func.date(Prediction.predicted_at) == today
                ).scalar() or 0
            ),
        },
    }


# ─── GET /api/reports/by-district ────────────────────────
@router.get("/by-district")
def get_report_by_district(
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    rows = db.query(
        Complaint.victim_district,
        func.count(Complaint.id).label("total_complaints"),
        func.sum(Complaint.amount_lost).label("total_amount_lost"),
        func.count(Complaint.id).filter(Complaint.alert_level == "HIGH").label("high_alert_count"),
    ).group_by(Complaint.victim_district).all()

    data = [
        {
            "district": r.victim_district or "Unknown",
            "total_complaints": r.total_complaints,
            "total_amount_lost": float(r.total_amount_lost) if r.total_amount_lost else 0,
            "high_alert_count": r.high_alert_count,
        }
        for r in rows
    ]

    if format == "csv":
        return _to_csv(data)
    return {"report_type": "by_district", "generated_at": str(datetime.utcnow()), "data": data}


# ─── GET /api/reports/by-bank ─────────────────────────────
@router.get("/by-bank")
def get_report_by_bank(
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    rows = db.query(
        Complaint.beneficiary_bank,
        func.count(Complaint.id).label("total_complaints"),
        func.sum(Complaint.amount_lost).label("total_amount_lost"),
    ).group_by(Complaint.beneficiary_bank).all()

    data = [
        {
            "bank": r.beneficiary_bank or "Unknown",
            "total_complaints": r.total_complaints,
            "total_amount_lost": float(r.total_amount_lost) if r.total_amount_lost else 0,
        }
        for r in rows
    ]

    if format == "csv":
        return _to_csv(data)
    return {"report_type": "by_bank", "generated_at": str(datetime.utcnow()), "data": data}


# ─── GET /api/reports/by-fraud-type ──────────────────────
@router.get("/by-fraud-type")
def get_report_by_fraud_type(
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    rows = db.query(
        Complaint.fraud_type,
        func.count(Complaint.id).label("total_complaints"),
        func.sum(Complaint.amount_lost).label("total_amount_lost"),
        func.avg(Complaint.number_of_hops).label("avg_hops"),
    ).group_by(Complaint.fraud_type).all()

    data = [
        {
            "fraud_type": r.fraud_type or "Unknown",
            "total_complaints": r.total_complaints,
            "total_amount_lost": float(r.total_amount_lost) if r.total_amount_lost else 0,
            "avg_hops": round(float(r.avg_hops), 1) if r.avg_hops else 0,
        }
        for r in rows
    ]

    if format == "csv":
        return _to_csv(data)
    return {"report_type": "by_fraud_type", "generated_at": str(datetime.utcnow()), "data": data}