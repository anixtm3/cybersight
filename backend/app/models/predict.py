import pickle
import math
import os
import numpy as np
import pandas as pd
import shap

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'ML', 'model.pkl')

_MODEL_PKG = None

def _load_model_pkg():
    global _MODEL_PKG
    if _MODEL_PKG is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(
                f"model.pkl not found at {MODEL_PATH}. "
                f"Place ML/model.pkl at repo root before starting server."
            )
        with open(MODEL_PATH, 'rb') as f:
            _MODEL_PKG = pickle.load(f)
    return _MODEL_PKG


FEATURE_ORDER = [
    'fraud_type_enc', 'amount_lost', 'number_of_hops',
    'victim_lat', 'victim_lon', 'bank_enc', 'account_age_days',
    'mule_network_flag', 'is_festival_period', 'hour_of_day_sin',
    'hour_of_day_cos', 'day_of_week', 'is_weekend',
    'rolling_6h_complaint_count', 'district_risk_score',
    'atm_density', 'time_since_last_complaint_same_bank',
    'victim_to_withdrawal_distance_km', 'district_enc'
]

_explainer = None
def _get_explainer(model):
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(model)
    return _explainer


def safe_encode(encoder, value, field_name: str = "value"):
    try:
        return int(encoder.transform([value])[0])
    except ValueError:
        print(f"[safe_encode] Unseen {field_name}: {value!r} — fallback 0")
        return 0


def _extract_shap_row(shap_raw, class_idx: int):
    if isinstance(shap_raw, list):
        row = np.asarray(shap_raw[class_idx][0])
    else:
        arr = np.asarray(shap_raw)
        if arr.ndim == 3:
            row = arr[0, :, class_idx]
        elif arr.ndim == 2:
            row = arr[0]
        else:
            raise ValueError(f"Unexpected SHAP ndim={arr.ndim}, shape={arr.shape}")
    if len(row) != len(FEATURE_ORDER):
        raise ValueError(f"SHAP row length {len(row)} != feature count {len(FEATURE_ORDER)}")
    return row


def get_top_atms_from_pkg(pkg, predicted_district: str, limit: int = 5):
    atm_df = pkg['atm_df']
    top5 = atm_df[atm_df['district'] == predicted_district].head(limit)
    return [
        {
            "atm_id": str(row["atm_id"]),
            "bank_name": str(row["bank_name"]),
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "district": str(row["district"]),
        }
        for _, row in top5.iterrows()
    ]


def predict(input_dict: dict) -> dict:
    pkg = _load_model_pkg()
    model = pkg['model']
    le_target = pkg['le_target']

    missing = [k for k in FEATURE_ORDER if k not in input_dict]
    if missing:
        raise ValueError(f"predict(): missing required features: {missing}")

    X = pd.DataFrame([input_dict])[FEATURE_ORDER]
    proba = model.predict_proba(X)[0]
    top_class_idx = int(np.argmax(proba))
    confidence = float(proba[top_class_idx])
    predicted_district = le_target.inverse_transform([top_class_idx])[0]

    if confidence >= 0.7:
        risk_level = "HIGH"
    elif confidence >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    action_map = {
        "HIGH": "Immediate freeze recommended — dispatch to nearest ATM cluster",
        "MEDIUM": "Monitor and alert bank nodal officer",
        "LOW": "Log for analyst review",
    }
    recommended_action = action_map[risk_level]

    try:
        explainer = _get_explainer(model)
        shap_raw = explainer.shap_values(X)
        shap_row = _extract_shap_row(shap_raw, top_class_idx)
        shap_values = {feat: float(val) for feat, val in zip(FEATURE_ORDER, shap_row)}
    except Exception as e:
        print(f"[predict] SHAP computation failed: {e}")
        shap_values = {}

    freezable_amount = round(float(input_dict['amount_lost']) * 0.6, 2)
    top_5_atms = get_top_atms_from_pkg(pkg, predicted_district)

    return {
        "predicted_district": predicted_district,
        "risk_level": risk_level,
        "confidence": confidence,
        "novel_pattern": confidence < 0.4,
        "recommended_action": recommended_action,
        "freezable_amount": freezable_amount,
        "shap_values": shap_values,
        "top_5_atms": top_5_atms,
        "withdrawal_window_minutes": 45,
    }


def get_encoders():
    pkg = _load_model_pkg()
    return pkg['le_fraud'], pkg['le_bank'], pkg['le_district']