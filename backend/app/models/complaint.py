from sqlalchemy import Column, Integer, String, Float, Numeric, Boolean, TIMESTAMP, Text, ARRAY, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from app.database import Base
import enum


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50), unique=True, nullable=False)
    tracking_number = Column(String(50), unique=True)
    fraud_type = Column(String(100))
    fraud_keywords = Column(ARRAY(Text))
    alert_level = Column(SAEnum('LOW', 'MEDIUM', 'HIGH', name='alert_level_enum'), default='LOW')
    victim_district = Column(String(100))
    victim_state = Column(String(100))
    victim_lat = Column(Float)
    victim_lon = Column(Float)
    amount_lost = Column(Numeric(15, 2))
    transaction_amount = Column(Numeric(15, 2))
    transaction_timestamp = Column(TIMESTAMP)
    victim_account_type = Column(String(50))
    beneficiary_account_type = Column(String(50))
    beneficiary_account = Column(String(100))
    beneficiary_bank = Column(String(200))
    upi_id = Column(String(100))
    mobile_number = Column(String(20))
    number_of_hops = Column(Integer, default=0)
    status = Column(String(50), default='pending')
    complaint_datetime = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ATMLocation(Base):
    __tablename__ = "atm_locations"

    id = Column(Integer, primary_key=True)
    atm_id = Column(String(50), unique=True, nullable=False)
    bank_name = Column(String(100))
    address = Column(Text)
    district = Column(String(100))
    state = Column(String(100))
    risk_score = Column(Numeric(5, 2), default=0)


class KeywordFraudMap(Base):
    __tablename__ = "keyword_fraud_map"

    keyword = Column(String(100), primary_key=True)
    fraud_type = Column(String(100), nullable=False)
    description = Column(Text)
    last_pattern_updated = Column(TIMESTAMP, server_default=func.now())
    pattern_data = Column(JSONB)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50))
    predicted_atm_id = Column(String(50))
    confidence_score = Column(Numeric(5, 2))
    predicted_lat = Column(Float)
    predicted_lon = Column(Float)
    radius_km = Column(Integer)
    risk_level = Column(SAEnum('LOW', 'MEDIUM', 'HIGH', name='risk_level_enum'))
    recommended_action = Column(Text)
    freezable_amount = Column(Numeric(15, 2))
    withdrawal_risk_window = Column(Text)
    shap_values = Column(JSONB)
    model_version = Column(String(50))
    alert_sent = Column(Boolean, default=False)
    predicted_at = Column(TIMESTAMP, server_default=func.now())


class AlertDispatchLog(Base):
    __tablename__ = "alert_dispatch_log"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50))
    alert_level = Column(SAEnum('LOW', 'MEDIUM', 'HIGH', name='alert_level_enum'))
    recipient_agency = Column(String(100))
    dispatch_status = Column(String(50))
    dispatched_at = Column(TIMESTAMP, server_default=func.now())


class MoneyRecoveryStatus(Base):
    __tablename__ = "money_recovery_status"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50))
    amount_lost = Column(Numeric)
    amount_withdrawn = Column(Numeric)
    amount_recoverable = Column(Numeric)
    recovery_status = Column(String(50))
    updated_at = Column(TIMESTAMP, server_default=func.now())


class MuleAccount(Base):
    __tablename__ = "mule_accounts"

    id = Column(Integer, primary_key=True)
    account_number = Column(String(100), unique=True, nullable=False)
    account_holder_name = Column(String(255))
    bank_name = Column(String(255))
    is_red_flagged = Column(Boolean, default=False)
    blockchain_tx_hash = Column(String(255))
    risk_score = Column(Float)
    transaction_chain = Column(JSONB)
    withdrawal_pattern = Column(Text)
    geographic_movement = Column(JSONB)
    red_flagged_by = Column(Text)
    red_flagged_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())


class MuleBlacklist(Base):
    __tablename__ = "mule_blacklist"

    id = Column(Integer, primary_key=True)
    account_number = Column(String(100), unique=True, nullable=False)
    blockchain_tx_hash = Column(String(255))
    flagged_by = Column(String(100))
    flagged_at = Column(TIMESTAMP, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='cyber_cell_officer')
    jurisdiction_district = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    token_hash = Column(Text, primary_key=True)
    revoked_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP)


class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id = Column(UUID(as_uuid=True), primary_key=True)
    admin_id = Column(Integer)
    action = Column(Text, nullable=False)
    target_id = Column(Text)
    ip_address = Column(Text)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    status = Column(Text)


class ReportMetadata(Base):
    __tablename__ = "report_metadata"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50))
    report_type = Column(String(50))
    generated_by = Column(String(100))
    software_contribution = Column(Text)
    generated_at = Column(TIMESTAMP, server_default=func.now())


# ─── NEW — added to match Saina's Day 2 schema (26 Aug) ────

class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50))
    officer_id = Column(Integer)
    note = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ActionLog(Base):
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50))
    officer_id = Column(Integer)
    action_type = Column(String(50))
    details = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class DispatchLog(Base):
    __tablename__ = "dispatch_log"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50))
    channel = Column(String(20), nullable=False)
    recipient = Column(Text, nullable=False)
    dispatched_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    delivery_status = Column(String(20))
    raw_response = Column(Text)


class RegistryProvenance(Base):
    __tablename__ = "registry_provenance"

    id = Column(Integer, primary_key=True)
    account_hash = Column(Text, nullable=False)
    tx_hash = Column(Text)
    flagging_authority = Column(Text)
    flag_basis = Column(String(30))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class WithdrawalHistory(Base):
    __tablename__ = "withdrawal_history"

    id = Column(Integer, primary_key=True)
    complaint_id = Column(String(50))
    atm_id = Column(String(50))
    withdrawal_lat = Column(Float)
    withdrawal_lon = Column(Float)
    withdrawal_time = Column(TIMESTAMP)
    cashout_channel = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())