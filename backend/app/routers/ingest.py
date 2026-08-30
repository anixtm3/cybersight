from app.crypto_utils import hash_account_number
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.complaint import Complaint, KeywordFraudMap, Prediction, DispatchLog, MuleAccount
from app.schemas.complaint import IngestRequest, IngestResponse
from app.rate_limit import limiter
from app.utils import generate_tracking_number
from datetime import datetime, timedelta
from app.routers.websocket import broadcast
from app.models.predict import predict as rishika_predict
import httpx

router = APIRouter(prefix="/api/complaints", tags=["ingest"])

BLOCKCHAIN_API = "http://localhost:8001"


# ─── Input sanity check ───────────────────────────────────
def validate_text(text: str, field_name: str = "field"):
    if not text:
        return
    if "\x00" in text:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid characters detected in {field_name}"
        )
    if len(text) > 5000:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} exceeds maximum allowed length"
        )


# ─── Keyword Detection ────────────────────────────────────
def detect_keywords(text: str, db: Session):
    if not text:
        return None, []

    text_lower = text.lower()
    keywords = db.query(KeywordFraudMap).all()

    matched_keywords = []
    fraud_type = None

    for kw in keywords:
        if kw.keyword in text_lower:
            matched_keywords.append(kw.keyword)
            if not fraud_type:
                fraud_type = kw.fraud_type

    return fraud_type, matched_keywords


# ─── Real Predict Wrapper ─────────────────────────────────
def call_predict(complaint_data: IngestRequest, db: Session):

    ts = complaint_data.transaction_timestamp or datetime.utcnow()
    ts_parsed = ts if isinstance(ts, datetime) else datetime.fromisoformat(str(ts))

    hour = ts_parsed.hour
    dow = ts_parsed.weekday()
    month = ts_parsed.month
    is_weekend = 1 if dow >= 5 else 0

    district = complaint_data.victim_district or ""

    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    complaints_6h = db.query(Complaint).filter(
        Complaint.victim_district == district,
        Complaint.complaint_datetime >= six_hours_ago
    ).count()

    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    complaints_24h = db.query(Complaint).filter(
        Complaint.victim_district == district,
        Complaint.complaint_datetime >= twenty_four_hours_ago
    ).count()

    input_dict = {
        "district":             district,
        "victim_lat":           complaint_data.victim_lat or 0.0,
        "victim_lon":           complaint_data.victim_lon or 0.0,
        "beneficiary_lat":      complaint_data.beneficiary_lat or complaint_data.victim_lat or 0.0,
        "beneficiary_lon":      complaint_data.beneficiary_lon or complaint_data.victim_lon or 0.0,
        "fraud_amount":         complaint_data.amount_lost or 0.0,
        "already_withdrawn":    0,
        "hour":                 hour,
        "dow":                  dow,
        "month":                month,
        "is_weekend":           is_weekend,
        "is_festival":          0,
        "is_holiday":           0,
        "complaints_6h":        complaints_6h,
        "complaints_24h":       complaints_24h,
        "district_risk_score":  0.5,
        "number_of_hops":       complaint_data.number_of_hops or 1,
        "fraud_keywords":       [],
        "transaction_timestamp": str(ts_parsed),
    }

    try:
        return rishika_predict(input_dict)
    except Exception as e:
        print(f"[call_predict] Model prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Model prediction failed. Please try again.")


# ─── Blockchain flag call — NON-BLOCKING ──────────────────
# FIX: Aniket's blockchain API hashes internally (keccak256 inside the
# Solidity contract). Sending a pre-hashed value here would cause the
# contract to hash an already-hashed string, and check()/lookup calls
# would never match the original account again. Confirmed directly
# with Aniket (2026-08-30) — send the RAW account_id, and the field
# name in the JSON payload must be "account_id", not "account_hash".
# hash_account_number() is intentionally NOT called here anymore.
def flag_mule_on_blockchain(
    account_id: str,
    risk_score: int,
    reason: str,
    authority: str = "CyberSight-AutoDispatch",
    evidence_basis: str = "ML_PREDICTION"
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


# ─── Ingest Endpoint ──────────────────────────────────────
@router.post("/ingest", response_model=IngestResponse)
@limiter.limit("100/hour")
async def ingest_complaint(complaint_data: IngestRequest, request: Request, db: Session = Depends(get_db)):
    complaint = None
    try:
        # 1. Input sanity check
        validate_text(complaint_data.complaint_text, "complaint_text")
        validate_text(complaint_data.victim_district, "victim_district")
        validate_text(complaint_data.victim_state, "victim_state")

        # 2. Duplicate check
        existing = db.query(Complaint).filter(
            Complaint.complaint_id == complaint_data.complaint_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Complaint ID already exists")

        # 3. Keyword detect karo
        fraud_type, matched_keywords = detect_keywords(complaint_data.complaint_text, db)

        if complaint_data.fraud_type:
            fraud_type = complaint_data.fraud_type

        if not fraud_type:
            fraud_type = "Unclassified"

        # 4. Complaint DB mein save karo
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

        # 5. Real ML predict
        try:
            prediction_data = call_predict(complaint_data, db)
        except HTTPException:
            complaint.status = "prediction_failed"
            db.commit()
            raise

        # 6. Alert level set karo
        alert_level = prediction_data["risk_level"]

        # 7. Alert level complaint mein update karo
        complaint.alert_level = alert_level
        db.commit()

        # 8. Prediction save karo
        prediction = Prediction(
            complaint_id=complaint_data.complaint_id,
            predicted_atm_id=prediction_data["predicted_atm_id"],
            predicted_lat=prediction_data["predicted_atm_lat"],
            predicted_lon=prediction_data["predicted_atm_lon"],
            confidence_score=prediction_data["fraud_probability"],
            risk_level=prediction_data["risk_level"],
            recommended_action=prediction_data["recommended_action"],
            withdrawal_risk_window=prediction_data["withdrawal_risk_window"],
            shap_values=prediction_data["shap_values"],
            freezable_amount=prediction_data["freezable_amount"]
        )
        db.add(prediction)
        db.commit()

        # 9. Alert dispatch log save karo
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

        # 10. HIGH alert pe blockchain mule flag — NON-BLOCKING
        if alert_level == "HIGH" and complaint_data.beneficiary_account:
            tx_hash = flag_mule_on_blockchain(
                account_id=complaint_data.beneficiary_account,
                risk_score=int(prediction_data["fraud_probability"] * 100),
                reason=f"{fraud_type or 'Unknown fraud'} — complaint {complaint.complaint_id}"
            )

            mule = db.query(MuleAccount).filter(
                MuleAccount.account_number == complaint_data.beneficiary_account
            ).first()

            if not mule:
                mule = MuleAccount(
                    account_number=complaint_data.beneficiary_account,
                    bank_name=complaint_data.beneficiary_bank,
                    is_red_flagged=True,
                    risk_score=prediction_data["fraud_probability"],
                    red_flagged_at=datetime.utcnow()
                )
                db.add(mule)
            else:
                mule.is_red_flagged = True
                mule.risk_score = prediction_data["fraud_probability"]
                mule.red_flagged_at = datetime.utcnow()

            if tx_hash:
                mule.blockchain_tx_hash = tx_hash

            db.commit()

        # 11. MEDIUM/HIGH alert broadcast karo
        if alert_level in ["MEDIUM", "HIGH"]:
            try:
                await broadcast({
                    "complaint_id": complaint.complaint_id,
                    "tracking_number": complaint.tracking_number,
                    "alert_level": alert_level,
                    "atm_id": prediction_data["predicted_atm_id"],
                    "atm_lat": prediction_data["predicted_atm_lat"],
                    "atm_lon": prediction_data["predicted_atm_lon"],
                    "recommended_action": prediction_data["recommended_action"],
                    "freezable_amount": prediction_data["freezable_amount"],
                    "timestamp": str(datetime.utcnow())
                })
            except Exception:
                pass

        return IngestResponse(
            complaint_id=complaint.complaint_id,
            tracking_number=complaint.tracking_number,
            fraud_type=fraud_type,
            alert_level=alert_level,
            predicted_atm_id=prediction_data["predicted_atm_id"],
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
            detail="An unexpected error occurred while processing the complaint. Please try again."
        )