from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models.complaint import Complaint, KeywordFraudMap, Prediction, DispatchLog, MuleAccount
from app.schemas.complaint import IngestRequest, IngestResponse
from app.rate_limit import limiter
from app.utils import generate_tracking_number
from datetime import datetime, timedelta
from app.routers.websocket import broadcast
from app.models.predict import predict as rishika_predict, safe_encode, get_encoders
import math
import httpx

router = APIRouter(prefix="/api/complaints", tags=["ingest"])

BLOCKCHAIN_API = "http://localhost:8001"


def validate_text(text_val: str, field_name: str = "field"):
    if not text_val:
        return
    if "\x00" in text_val:
        raise HTTPException(status_code=400, detail=f"Invalid characters detected in {field_name}")
    if len(text_val) > 5000:
        raise HTTPException(status_code=400, detail=f"{field_name} exceeds maximum allowed length")


def detect_keywords(text_val: str, db: Session):
    if not text_val:
        return None, []
    text_lower = text_val.lower()
    keywords = db.query(KeywordFraudMap).all()
    matched_keywords = []
    fraud_type = None
    for kw in keywords:
        if kw.keyword in text_lower:
            matched_keywords.append(kw.keyword)
            if not fraud_type:
                fraud_type = kw.fraud_type
    return fraud_type, matched_keywords


def call_predict(complaint_data: IngestRequest, db: Session):
    le_fraud, le_bank, le_district = get_encoders()

    ts = complaint_data.transaction_timestamp or datetime.utcnow()
    ts_parsed = ts if isinstance(ts, datetime) else datetime.fromisoformat(str(ts))

    hour = ts_parsed.hour
    dow = ts_parsed.weekday()
    is_weekend = 1 if dow >= 5 else 0

    district = complaint_data.victim_district or ""
    fraud_type = complaint_data.fraud_type or "Unclassified"
    bank = complaint_data.beneficiary_bank or ""
    vlat = float(complaint_data.victim_lat or 0.0)
    vlon = float(complaint_data.victim_lon or 0.0)

    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    rolling_6h_complaint_count = db.query(Complaint).filter(
        Complaint.victim_district == district,
        Complaint.complaint_datetime >= six_hours_ago
    ).count()

    row = db.execute(
        text("SELECT AVG(district_risk_score) AS avg_score FROM complaints WHERE victim_district = :d"),
        {"d": district}
    ).first()
    district_risk_score = float(row.avg_score) if row and row.avg_score is not None else 0.5

    atm_row = db.execute(
        text("""
            SELECT COUNT(*) AS cnt FROM atm_locations
            WHERE ST_DWithin(
                location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                5000
            )
        """),
        {"lon": vlon, "lat": vlat}
    ).first()
    atm_density = int(atm_row.cnt) if atm_row and atm_row.cnt is not None else 5

    tb_row = db.execute(
        text("""
            SELECT EXTRACT(EPOCH FROM (NOW() - MAX(complaint_datetime)))/3600 AS hrs
            FROM complaints WHERE beneficiary_bank = :bank
        """),
        {"bank": bank}
    ).first()
    time_since_last_complaint_same_bank = float(tb_row.hrs) if tb_row and tb_row.hrs is not None else -1.0

    input_dict = {
        "fraud_type_enc": safe_encode(le_fraud, fraud_type, "fraud_type"),
        "amount_lost": float(complaint_data.amount_lost or 0.0),
        "number_of_hops": int(complaint_data.number_of_hops or 1),
        "victim_lat": vlat,
        "victim_lon": vlon,
        "bank_enc": safe_encode(le_bank, bank, "beneficiary_bank"),
        "account_age_days": 180,
        "mule_network_flag": 1 if (complaint_data.number_of_hops or 1) >= 4 else 0,
        "is_festival_period": 0,
        "hour_of_day_sin": math.sin(2 * math.pi * hour / 24),
        "hour_of_day_cos": math.cos(2 * math.pi * hour / 24),
        "day_of_week": dow,
        "is_weekend": is_weekend,
        "rolling_6h_complaint_count": rolling_6h_complaint_count,
        "district_risk_score": district_risk_score,
        "atm_density": atm_density,
        "time_since_last_complaint_same_bank": time_since_last_complaint_same_bank,
        "victim_to_withdrawal_distance_km": 0.0,
        "district_enc": safe_encode(le_district, district, "victim_district"),
    }

    try:
        result = rishika_predict(input_dict)
    except HTTPException:
        raise
    except RuntimeError as e:
        print(f"[call_predict] Model unavailable: {str(e)}")
        raise HTTPException(status_code=503, detail="Prediction model is not available right now.")
    except Exception as e:
        print(f"[call_predict] Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Model prediction failed. Please try again.")

    return result


def flag_mule_on_blockchain(
    account_id: str,
    risk_score: int,
    reason: str,
    authority: str = "CyberSight-AutoDispatch",
    evidence_basis: str = "MONITORING_SUSPECTED"
):
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(
                f"{BLOCKCHAIN_API}/api/blockchain/flag",
                json={
                    "account_id": account_id,
                    "flagging_authority": authority,
                    "evidence_basis": evidence_basis,
                    "risk_score": risk_score,
                    "reason": reason
                }
            )
            if resp.status_code == 200:
                return resp.json().get("tx_hash")
            return None
    except httpx.RequestError:
        return None
    except Exception:
        return None


@router.post("/ingest", response_model=IngestResponse)
@limiter.limit("100/hour")
async def ingest_complaint(complaint_data: IngestRequest, request: Request, db: Session = Depends(get_db)):
    complaint = None
    try:
        validate_text(complaint_data.complaint_text, "complaint_text")
        validate_text(complaint_data.victim_district, "victim_district")
        validate_text(complaint_data.victim_state, "victim_state")

        existing = db.query(Complaint).filter(
            Complaint.complaint_id == complaint_data.complaint_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Complaint ID already exists")

        fraud_type, matched_keywords = detect_keywords(complaint_data.complaint_text, db)
        if complaint_data.fraud_type:
            fraud_type = complaint_data.fraud_type
        if not fraud_type:
            fraud_type = "Unclassified"

        complaint = Complaint(
            complaint_id=complaint_data.complaint_id,
            fraud_type=fraud_type,
            fraud_keywords=matched_keywords if matched_keywords else None,
            victim_district=complaint_data.victim_district,
            victim_state=complaint_data.victim_state,
            victim_lat=complaint_data.victim_lat,
            victim_lon=complaint_data.victim_lon,
            victim_account_type=complaint_data.victim_account_type,
            mobile_number=complaint_data.mobile_number,
            beneficiary_account=complaint_data.beneficiary_account,
            beneficiary_bank=complaint_data.beneficiary_bank,
            beneficiary_account_type=complaint_data.beneficiary_account_type,
            beneficiary_lat=complaint_data.beneficiary_lat,
            beneficiary_lon=complaint_data.beneficiary_lon,
            transaction_amount=complaint_data.transaction_amount,
            amount_lost=complaint_data.amount_lost,
            number_of_hops=complaint_data.number_of_hops,
            upi_id=complaint_data.upi_id,
            status="pending",
            complaint_datetime=datetime.utcnow()
        )
        complaint.tracking_number = generate_tracking_number(db)

        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        try:
            prediction_data = call_predict(complaint_data, db)
        except HTTPException:
            complaint.status = "prediction_failed"
            db.commit()
            raise

        alert_level = prediction_data["risk_level"]
        complaint.alert_level = alert_level
        db.commit()

        top_atms = prediction_data.get("top_5_atms") or []
        primary_atm = top_atms[0] if top_atms else None

        prediction = Prediction(
            complaint_id=complaint_data.complaint_id,
            predicted_atm_id=primary_atm["atm_id"] if primary_atm else None,
            predicted_lat=primary_atm["lat"] if primary_atm else None,
            predicted_lon=primary_atm["lon"] if primary_atm else None,
            confidence_score=prediction_data["confidence"],
            risk_level=prediction_data["risk_level"],
            recommended_action=prediction_data["recommended_action"],
            withdrawal_risk_window=prediction_data["withdrawal_window_minutes"],
            shap_values=prediction_data["shap_values"],
            freezable_amount=prediction_data["freezable_amount"]
        )
        db.add(prediction)
        db.commit()

        if alert_level in ["MEDIUM", "HIGH"]:
            agencies = ["I4C", "CyberCell", "Bank", "PoliceSHO"]
            for agency in agencies:
                dispatch_log = DispatchLog(
                    complaint_id=complaint.complaint_id,
                    channel="webhook",
                    recipient=agency,
                    delivery_status="sent",
                    raw_response=None
                )
                db.add(dispatch_log)
            db.commit()

        if alert_level == "HIGH" and complaint_data.beneficiary_account:
            tx_hash = flag_mule_on_blockchain(
                account_id=complaint_data.beneficiary_account,
                risk_score=int(prediction_data["confidence"] * 100),
                reason=f"{fraud_type} — complaint {complaint.complaint_id}",
                evidence_basis="INVESTIGATION_VERIFIED"
            )

            mule = db.query(MuleAccount).filter(
                MuleAccount.account_number == complaint_data.beneficiary_account
            ).first()

            if not mule:
                mule = MuleAccount(
                    account_number=complaint_data.beneficiary_account,
                    bank_name=complaint_data.beneficiary_bank,
                    is_red_flagged=True,
                    risk_score=prediction_data["confidence"],
                    red_flagged_at=datetime.utcnow()
                )
                db.add(mule)
            else:
                mule.is_red_flagged = True
                mule.risk_score = prediction_data["confidence"]
                mule.red_flagged_at = datetime.utcnow()

            if tx_hash:
                mule.blockchain_tx_hash = tx_hash

            db.commit()

        if alert_level in ["MEDIUM", "HIGH"]:
            try:
                await broadcast({
                    "complaint_id": complaint.complaint_id,
                    "tracking_number": complaint.tracking_number,
                    "alert_level": alert_level,
                    "atm_id": primary_atm["atm_id"] if primary_atm else None,
                    "atm_lat": primary_atm["lat"] if primary_atm else None,
                    "atm_lon": primary_atm["lon"] if primary_atm else None,
                    "recommended_action": prediction_data["recommended_action"],
                    "freezable_amount": prediction_data["freezable_amount"],
                    "timestamp": str(datetime.utcnow()),
                    "dispatch_status": {
                        "sms": "pending",
                        "email": "pending",
                        "webhook": "sent",
                        "dashboard": "sent"
                    }
                })
            except Exception:
                pass

        return IngestResponse(
            complaint_id=complaint.complaint_id,
            tracking_number=complaint.tracking_number,
            fraud_type=fraud_type,
            alert_level=alert_level,
            predicted_atm_id=primary_atm["atm_id"] if primary_atm else None,
            message="Complaint ingested successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ingest_complaint] Unexpected error: {str(e)}")
        if complaint is not None:
            try:
                complaint.status = "prediction_failed"
                db.commit()
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )