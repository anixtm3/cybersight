-- =====================================================
-- CyberSight AI — Final Database Schema
-- Project: PS 26184 | MHA / I4C | SIH 2026
-- Engineer: Saina Sharma
-- Version: Day 2 (Updated)
-- =====================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================================
-- ENUM TYPES
-- =====================================================

DO $$ BEGIN
    CREATE TYPE alert_level_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE risk_level_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- =====================================================
-- USERS
-- Three roles: admin, cyber_cell_officer, bank_nodal_officer
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    id                    SERIAL PRIMARY KEY,
    username              VARCHAR(100) UNIQUE NOT NULL,
    password_hash         VARCHAR(255) NOT NULL,
    role                  VARCHAR(50) DEFAULT 'cyber_cell_officer'
                          CHECK (role IN ('admin', 'cyber_cell_officer', 'bank_nodal_officer')),
    jurisdiction_district TEXT,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TRACKING NUMBER — auto-generate on INSERT
-- =====================================================

CREATE SEQUENCE IF NOT EXISTS tracking_number_seq START 1;

CREATE OR REPLACE FUNCTION generate_tracking_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tracking_number :=
        'CS-' ||
        EXTRACT(YEAR FROM CURRENT_DATE)::TEXT ||
        '-' ||
        LPAD(nextval('tracking_number_seq')::TEXT, 5, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMPLAINTS
-- Core NCRP complaint table
-- =====================================================

CREATE TABLE IF NOT EXISTS complaints (
    id                      SERIAL PRIMARY KEY,
    complaint_id            VARCHAR(50) UNIQUE NOT NULL,
    tracking_number         VARCHAR(50) UNIQUE,

    fraud_type              VARCHAR(100) NOT NULL,
    fraud_keywords          TEXT[],

    victim_district         VARCHAR(100),
    victim_state            VARCHAR(100),
    victim_lat              DOUBLE PRECISION,
    victim_lon              DOUBLE PRECISION,
    victim_location         GEOMETRY(Point, 4326),

    amount_lost             NUMERIC(15, 2),
    transaction_amount      NUMERIC(15, 2),
    transaction_timestamp   TIMESTAMP,

    victim_account_type     VARCHAR(50),
    beneficiary_account_type VARCHAR(50),
    beneficiary_account     VARCHAR(100),
    beneficiary_bank        VARCHAR(200),
    upi_id                  VARCHAR(100),
    mobile_number           VARCHAR(20),

    alert_level             alert_level_enum DEFAULT 'LOW',
    number_of_hops          INTEGER DEFAULT 0,

    status                  VARCHAR(50) DEFAULT 'pending',
    complaint_datetime      TIMESTAMP,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_tracking_number ON complaints;
CREATE TRIGGER trg_tracking_number
    BEFORE INSERT ON complaints
    FOR EACH ROW
    WHEN (NEW.tracking_number IS NULL)
    EXECUTE FUNCTION generate_tracking_number();

-- =====================================================
-- ATM LOCATIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS atm_locations (
    id         SERIAL PRIMARY KEY,
    atm_id     VARCHAR(50) UNIQUE NOT NULL,
    bank_name  VARCHAR(100),
    address    TEXT,
    district   VARCHAR(100),
    state      VARCHAR(100),
    location   GEOMETRY(Point, 4326),
    risk_score NUMERIC(5, 2) DEFAULT 0
);

-- =====================================================
-- KEYWORD FRAUD MAP
-- =====================================================

CREATE TABLE IF NOT EXISTS keyword_fraud_map (
    keyword              VARCHAR(100) PRIMARY KEY,
    fraud_type           VARCHAR(100) NOT NULL,
    description          TEXT,
    last_pattern_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pattern_data         JSONB
);

INSERT INTO keyword_fraud_map (keyword, fraud_type, description) VALUES
    ('olx',            'OLX Scam',           'OLX marketplace fraud'),
    ('second hand',    'OLX Scam',           'Second hand goods scam'),
    ('upi',            'UPI Fraud',          'UPI payment fraud'),
    ('phonepe',        'UPI Fraud',          'PhonePe fraud'),
    ('gpay',           'UPI Fraud',          'Google Pay fraud'),
    ('qr',             'QR Code Scam',       'QR code payment scam'),
    ('scan',           'QR Code Scam',       'Scan and pay scam'),
    ('kyc',            'KYC Fraud',          'KYC update fraud'),
    ('investment',     'Investment Scam',    'Investment return fraud'),
    ('high returns',   'Investment Scam',    'High return investment scam'),
    ('job offer',      'Job Fraud',          'Fake job offer fraud'),
    ('work from home', 'Job Fraud',          'Work from home scam'),
    ('lottery',        'Lottery Fraud',      'Lottery winning fraud'),
    ('prize',          'Lottery Fraud',      'Prize money fraud'),
    ('tech support',   'Tech Support Fraud', 'Fake tech support fraud'),
    ('romance',        'Romance Scam',       'Romance / dating scam'),
    ('sim swap',       'SIM Swap Fraud',     'SIM swap fraud')
ON CONFLICT (keyword) DO NOTHING;

-- =====================================================
-- PREDICTIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS predictions (
    id                    SERIAL PRIMARY KEY,
    complaint_id          VARCHAR(50) REFERENCES complaints(complaint_id),
    predicted_atm_id      VARCHAR(50) REFERENCES atm_locations(atm_id),
    confidence_score      NUMERIC(5, 2),
    predicted_lat         DOUBLE PRECISION,
    predicted_lon         DOUBLE PRECISION,
    radius_km             INTEGER,
    risk_level            risk_level_enum,
    recommended_action    TEXT,
    freezable_amount      NUMERIC(15, 2),
    withdrawal_risk_window TEXT,
    shap_values           JSONB,
    model_version         VARCHAR(50),
    alert_sent            BOOLEAN DEFAULT FALSE,
    predicted_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ALERTS
-- =====================================================

CREATE TABLE IF NOT EXISTS alerts (
    id           SERIAL PRIMARY KEY,
    complaint_id VARCHAR(50) REFERENCES complaints(complaint_id),
    alert_type   VARCHAR(50),
    message      TEXT,
    sent_to      VARCHAR(200),
    sent_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status       VARCHAR(50) DEFAULT 'sent'
);

-- =====================================================
-- ALERT DISPATCH LOG
-- =====================================================

CREATE TABLE IF NOT EXISTS alert_dispatch_log (
    id               SERIAL PRIMARY KEY,
    complaint_id     VARCHAR(50) REFERENCES complaints(complaint_id),
    alert_level      alert_level_enum,
    recipient_agency VARCHAR(100),
    dispatch_status  VARCHAR(50),
    dispatched_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MONEY RECOVERY STATUS
-- =====================================================

CREATE TABLE IF NOT EXISTS money_recovery_status (
    id                  SERIAL PRIMARY KEY,
    complaint_id        VARCHAR(50) REFERENCES complaints(complaint_id),
    amount_lost         NUMERIC(15, 2),
    amount_withdrawn    NUMERIC(15, 2),
    amount_recoverable  NUMERIC(15, 2),
    recovery_status     VARCHAR(50),
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MULE ACCOUNTS
-- =====================================================

CREATE TABLE IF NOT EXISTS mule_accounts (
    id                   SERIAL PRIMARY KEY,
    account_number       VARCHAR(100) UNIQUE NOT NULL,
    account_holder_name  VARCHAR(255),
    bank_name            VARCHAR(255),
    is_red_flagged       BOOLEAN DEFAULT FALSE,
    blockchain_tx_hash   VARCHAR(255),
    risk_score           DOUBLE PRECISION,
    transaction_chain    JSONB,
    withdrawal_pattern   TEXT,
    geographic_movement  JSONB,
    red_flagged_by       TEXT,
    red_flagged_at       TIMESTAMP,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MULE BLACKLIST
-- =====================================================

CREATE TABLE IF NOT EXISTS mule_blacklist (
    id                 SERIAL PRIMARY KEY,
    account_number     VARCHAR(100) UNIQUE NOT NULL,
    blockchain_tx_hash VARCHAR(255),
    flagged_by         VARCHAR(100),
    flagged_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- WITHDRAWAL HISTORY
-- =====================================================

CREATE TABLE IF NOT EXISTS withdrawal_history (
    id               SERIAL PRIMARY KEY,
    complaint_id     VARCHAR(50) REFERENCES complaints(complaint_id),
    atm_id           VARCHAR(50) REFERENCES atm_locations(atm_id),
    withdrawal_lat   DOUBLE PRECISION,
    withdrawal_lon   DOUBLE PRECISION,
    withdrawal_time  TIMESTAMP,
    cashout_channel  VARCHAR(50),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- REPORT METADATA
-- =====================================================

CREATE TABLE IF NOT EXISTS report_metadata (
    id                    SERIAL PRIMARY KEY,
    complaint_id          VARCHAR(50),
    report_type           VARCHAR(50),
    generated_by          VARCHAR(100),
    software_contribution TEXT,
    generated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CASE NOTES — Evidence documentation
-- =====================================================

CREATE TABLE IF NOT EXISTS case_notes (
    id           SERIAL PRIMARY KEY,
    complaint_id VARCHAR(50) REFERENCES complaints(complaint_id),
    officer_id   INT REFERENCES users(id),
    note         TEXT NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- =====================================================
-- ACTION LOG — Officer actions per case
-- =====================================================

CREATE TABLE IF NOT EXISTS action_log (
    id           SERIAL PRIMARY KEY,
    complaint_id VARCHAR(50) REFERENCES complaints(complaint_id),
    officer_id   INT REFERENCES users(id),
    action_type  VARCHAR(50),
    details      TEXT,
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- =====================================================
-- DISPATCH LOG — Alert channel tracking
-- =====================================================

CREATE TABLE IF NOT EXISTS dispatch_log (
    id               SERIAL PRIMARY KEY,
    complaint_id     VARCHAR(50) REFERENCES complaints(complaint_id),
    channel          VARCHAR(20) NOT NULL,
    recipient        TEXT NOT NULL,
    dispatched_at    TIMESTAMPTZ DEFAULT now(),
    delivery_status  VARCHAR(20),
    raw_response     TEXT
);

-- =====================================================
-- REGISTRY PROVENANCE — Blockchain evidence
-- =====================================================

CREATE TABLE IF NOT EXISTS registry_provenance (
    id                SERIAL PRIMARY KEY,
    account_hash      TEXT NOT NULL,
    tx_hash           TEXT,
    flagging_authority TEXT,
    flag_basis        VARCHAR(30),
    created_at        TIMESTAMPTZ DEFAULT now()
);

-- =====================================================
-- SECURITY — JWT token revocation
-- =====================================================

CREATE TABLE IF NOT EXISTS revoked_tokens (
    token_hash TEXT PRIMARY KEY,
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- =====================================================
-- SECURITY — Audit log
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_log (
    log_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id   INTEGER REFERENCES users(id),
    action     TEXT NOT NULL,
    target_id  TEXT,
    ip_address TEXT,
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status     TEXT
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_atm_locations_geom
    ON atm_locations USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_complaints_victim_location
    ON complaints USING GIST(victim_location);

CREATE INDEX IF NOT EXISTS idx_complaints_alert_level
    ON complaints(alert_level);

CREATE INDEX IF NOT EXISTS idx_complaints_fraud_type
    ON complaints(fraud_type);

CREATE INDEX IF NOT EXISTS idx_complaints_tracking_number
    ON complaints(tracking_number);

CREATE INDEX IF NOT EXISTS idx_predictions_atm_id
    ON predictions(predicted_atm_id);

CREATE INDEX IF NOT EXISTS idx_audit_log_admin
    ON audit_log(admin_id);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
    ON audit_log(timestamp);

CREATE INDEX IF NOT EXISTS idx_revoked_tokens_expires_at
    ON revoked_tokens(expires_at);

   