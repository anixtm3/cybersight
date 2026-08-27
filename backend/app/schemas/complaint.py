from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ─── COMPLAINT ───────────────────────────────────────────

class ComplaintCreate(BaseModel):
    complaint_id: str
    fraud_type: Optional[str] = None
    fraud_keywords: Optional[List[str]] = None
    alert_level: Optional[AlertLevel] = AlertLevel.LOW

    victim_district: Optional[str] = None
    victim_state: Optional[str] = None
    victim_lat: Optional[float] = None
    victim_lon: Optional[float] = None

    victim_account_type: Optional[str] = None
    mobile_number: Optional[str] = None
    upi_id: Optional[str] = None

    beneficiary_account: Optional[str] = None
    beneficiary_bank: Optional[str] = None
    beneficiary_account_type: Optional[str] = None

    transaction_amount: Optional[float] = None
    transaction_timestamp: Optional[datetime] = None
    amount_lost: Optional[float] = None
    number_of_hops: Optional[int] = None

    complaint_datetime: Optional[datetime] = None


class ComplaintResponse(BaseModel):
    id: int
    complaint_id: str
    tracking_number: Optional[str] = None
    fraud_type: Optional[str] = None
    fraud_keywords: Optional[List[str]] = None
    alert_level: Optional[AlertLevel] = None
    victim_district: Optional[str] = None
    victim_state: Optional[str] = None
    victim_lat: Optional[float] = None
    victim_lon: Optional[float] = None
    victim_account_type: Optional[str] = None
    mobile_number: Optional[str] = None
    upi_id: Optional[str] = None
    beneficiary_account: Optional[str] = None
    beneficiary_bank: Optional[str] = None
    beneficiary_account_type: Optional[str] = None
    transaction_amount: Optional[float] = None
    transaction_timestamp: Optional[datetime] = None
    amount_lost: Optional[float] = None
    number_of_hops: Optional[int] = None
    status: Optional[str] = None
    complaint_datetime: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── PREDICTION ──────────────────────────────────────────

class PredictionResponse(BaseModel):
    complaint_id: str
    predicted_atm_id: Optional[str] = None
    predicted_lat: Optional[float] = None
    predicted_lon: Optional[float] = None
    confidence_score: Optional[float] = None
    risk_level: Optional[AlertLevel] = None
    recommended_action: Optional[str] = None
    withdrawal_risk_window: Optional[str] = None
    shap_values: Optional[dict] = None
    freezable_amount: Optional[float] = None

    class Config:
        from_attributes = True


# ─── INGEST ──────────────────────────────────────────────

class IngestRequest(BaseModel):
    complaint_id: str
    complaint_text: Optional[str] = None
    fraud_type: Optional[str] = None
    victim_district: Optional[str] = None
    victim_state: Optional[str] = None
    victim_lat: Optional[float] = None
    victim_lon: Optional[float] = None
    beneficiary_lat: Optional[float] = None
    beneficiary_lon: Optional[float] = None
    victim_account_type: Optional[str] = None
    mobile_number: Optional[str] = None
    beneficiary_account: Optional[str] = None
    beneficiary_bank: Optional[str] = None
    beneficiary_account_type: Optional[str] = None
    transaction_amount: Optional[float] = None
    transaction_timestamp: Optional[datetime] = None
    amount_lost: Optional[float] = None
    number_of_hops: Optional[int] = None
    upi_id: Optional[str] = None


class IngestResponse(BaseModel):
    complaint_id: str
    tracking_number: str
    fraud_type: Optional[str] = None
    alert_level: str
    predicted_atm_id: Optional[str] = None
    message: str


# ─── HEATMAP ─────────────────────────────────────────────

class HeatmapResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[dict]


# ─── AUTH ────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "admin"
    expires_in: str = "8 hours"

    # ─── EVIDENCE (case notes / action log) ─────────────────

class CaseNoteCreate(BaseModel):
    note: str


class CaseNoteResponse(BaseModel):
    id: int
    complaint_id: str
    officer_id: int
    note: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ActionLogCreate(BaseModel):
    action_type: str
    details: Optional[str] = None


class ActionLogResponse(BaseModel):
    id: int
    complaint_id: str
    officer_id: int
    action_type: str
    details: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True