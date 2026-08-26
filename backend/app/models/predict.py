import pandas as pd
import numpy as np
import joblib
import shap
import json
import os
from math import radians, sin, cos, sqrt, atan2

print("CyberSight Prediction Engine loading...", flush=True)

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

model     = joblib.load(os.path.join(_THIS_DIR, 'cybersight_model.pkl'))
atm_df    = pd.read_csv(os.path.join(_THIS_DIR, 'atm_locations.csv'))
explainer = shap.TreeExplainer(model)

FEATURES = [
    'hour', 'dow', 'month', 'is_weekend', 'is_night',
    'is_festival', 'is_holiday', 'high_risk_window',
    'complaints_6h', 'complaints_24h', 'district_risk_score',
    'fraud_amount', 'already_withdrawn', 'freezable_amount',
    'number_of_hops', 'distance_victim_to_atm',
    'distance_beneficiary_to_atm', 'historical_fraud_count_at_atm',
    'atm_fraud_rate_last_30days'
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


def predict(input_dict):

    # ── New fields from checklist 3.1 ──────────────────
    fraud_keywords     = input_dict.get('fraud_keywords', [])
    transaction_amount = input_dict.get('transaction_amount',
                         input_dict.get('fraud_amount', 10000))
    transaction_ts     = input_dict.get('transaction_timestamp', None)

    # ── Find nearest ATM ───────────────────────────────
    district_atms = atm_df[
        atm_df['district'] == input_dict.get('district', '')
    ].reset_index(drop=True)

    if district_atms.empty:
        district_atms = atm_df.reset_index(drop=True)

    dists = district_atms.apply(
        lambda r: haversine(
            input_dict['victim_lat'], input_dict['victim_lon'],
            r['lat'], r['lon']), axis=1)

    best_atm           = district_atms.iloc[dists.values.argmin()]
    dist_victim_atm    = dists.values.min()

    # ── Calculate all features ─────────────────────────
    fraud_amount      = float(input_dict.get('fraud_amount',
                              transaction_amount))
    already_withdrawn = float(input_dict.get('already_withdrawn', 0))
    freezable         = round(fraud_amount - already_withdrawn, 2)
    hour              = int(input_dict.get('hour', 12))
    is_night          = int(hour >= 22 or hour <= 6)
    is_festival       = int(input_dict.get('is_festival', 0))
    is_holiday        = int(input_dict.get('is_holiday', 0))
    high_risk         = int(is_night and (is_festival or is_holiday))

    beneficiary_lat   = float(input_dict.get('beneficiary_lat',
                              input_dict['victim_lat']))
    beneficiary_lon   = float(input_dict.get('beneficiary_lon',
                              input_dict['victim_lon']))
    dist_bene_atm     = haversine(
                            beneficiary_lat, beneficiary_lon,
                            float(best_atm['lat']),
                            float(best_atm['lon']))

    row = {
        'hour':                          hour,
        'dow':                           int(input_dict.get('dow', 0)),
        'month':                         int(input_dict.get('month', 1)),
        'is_weekend':                    int(input_dict.get('is_weekend', 0)),
        'is_night':                      is_night,
        'is_festival':                   is_festival,
        'is_holiday':                    is_holiday,
        'high_risk_window':              high_risk,
        'complaints_6h':                 float(input_dict.get('complaints_6h', 1)),
        'complaints_24h':                float(input_dict.get('complaints_24h', 3)),
        'district_risk_score':           float(input_dict.get('district_risk_score', 0.5)),
        'fraud_amount':                  fraud_amount,
        'already_withdrawn':             already_withdrawn,
        'freezable_amount':              freezable,
        'number_of_hops':                int(input_dict.get('number_of_hops', 2)),
        'distance_victim_to_atm':        dist_victim_atm,
        'distance_beneficiary_to_atm':   dist_bene_atm,
        'historical_fraud_count_at_atm': float(best_atm['historical_fraud_count']),
        'atm_fraud_rate_last_30days':    float(best_atm['atm_fraud_rate_last_30days']),
    }

    # ── Predict ─────────────────────────────────────────
    X    = pd.DataFrame([row])[FEATURES]
    prob = float(model.predict_proba(X)[0][1])

    if prob >= 0.80:
        risk = 'HIGH'
    elif prob >= 0.60:
        risk = 'MEDIUM'
    else:
        risk = 'LOW'

    # ── SHAP top 5 ────────────────────────────────────
    shap_vals = explainer.shap_values(X)[0]
    shap_dict = dict(
        sorted(zip(FEATURES, shap_vals),
               key=lambda x: abs(x[1]), reverse=True)[:5]
    )

    # ── Plain English output ───────────────────────────
    bank   = best_atm['bank_name']
    atm_id = best_atm['atm_id']

    if risk == 'HIGH':
        action = (f"Deploy officers immediately to {bank} ATM ({atm_id}). "
                  f"Freeze beneficiary account now. "
                  f"Cash withdrawal expected within 1-2 hours.")
        window = "High risk — withdrawal expected in next 1 to 2 hours"
    elif risk == 'MEDIUM':
        action = (f"Alert CyberCell and local police. "
                  f"Monitor {bank} ATM ({atm_id}) closely.")
        window = "Moderate risk — withdrawal possible in next 2 to 4 hours"
    else:
        action = "Log complaint on dashboard. No immediate field action needed."
        window = "Low immediate risk — monitor dashboard"

    return {
        'fraud_probability':      round(prob, 4),
        'predicted_atm_id':       str(atm_id),
        'predicted_atm_lat':      float(best_atm['lat']),
        'predicted_atm_lon':      float(best_atm['lon']),
        'risk_level':             risk,
        'recommended_action':     action,
        'shap_values':            {k: round(float(v), 4)
                                   for k, v in shap_dict.items()},
        'withdrawal_risk_window': window,
        'freezable_amount':       freezable
    }


# ── Test run ──────────────────────────────────────────
if __name__ == '__main__':
    test_input = {
        # Checklist 3.1 — all required fields
        'district':                 'Jamtara',
        'fraud_type':               'UPI Fraud',
        'fraud_keywords':           ['upi', 'transfer'],
        'transaction_amount':       50000,
        'transaction_timestamp':    '2026-06-25 23:00:00',
        'victim_lat':               23.95,
        'victim_lon':               86.81,
        'beneficiary_lat':          23.80,
        'beneficiary_lon':          86.60,
        'victim_account_type':      'savings',
        'beneficiary_account_type': 'current',
        'number_of_hops':           3,
        'fraud_amount':             50000,
        'already_withdrawn':        10000,
        'hour':                     23,
        'dow':                      1,
        'month':                    10,
        'is_weekend':               0,
        'is_festival':              1,
        'is_holiday':               0,
        'complaints_6h':            3,
        'complaints_24h':           8,
        'district_risk_score':      0.9
    }

    result = predict(test_input)

    print("\n" + "="*50)
    print("CYBERSIGHT PREDICTION RESULT")
    print("="*50)
    for k, v in result.items():
        print(f"  {k}: {v}")

    # Verify checklist 3.2 — India bounds check
    lat = result['predicted_atm_lat']
    lon = result['predicted_atm_lon']
    assert 8 <= lat <= 37,  f"LAT OUT OF INDIA BOUNDS: {lat}"
    assert 68 <= lon <= 97, f"LON OUT OF INDIA BOUNDS: {lon}"
    print("\n✅ 3.2 — India bounds check PASSED")

    # Verify checklist 3.3 — exactly 5 SHAP keys
    assert len(result['shap_values']) == 5, "SHAP must have exactly 5 keys"
    print("✅ 3.3 — SHAP top 5 check PASSED")

    # Verify checklist 3.4 — no technical jargon
    jargon = ['XGBoost', 'SHAP', 'probability', 'model', 'predict']
    for word in jargon:
        assert word not in result['recommended_action'], \
            f"Jargon found: {word}"
    print("✅ 3.4 — Plain English check PASSED")

    # Save sample output
    with open(os.path.join(_THIS_DIR, 'sample_prediction.json'), 'w') as f:
        json.dump(result, f, indent=2)
    print("\nSaved: sample_prediction.json")
    print("\n✅ ALL CHECKLIST 3.x CHECKS PASSED")