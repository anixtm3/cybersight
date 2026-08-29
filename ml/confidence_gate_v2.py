import pandas as pd
import numpy as np
import joblib
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ============================================================
# 1. LOAD MODEL + DATA
# ============================================================
model = joblib.load("models/withdrawal_predictor.pkl")
le_fraud = joblib.load("models/le_fraud.pkl")
le_bank = joblib.load("models/le_bank.pkl")
le_district = joblib.load("models/le_district.pkl")

df = pd.read_csv("data/complaints_engineered.csv")

feature_cols = [
    'fraud_type_enc', 'amount_lost', 'number_of_hops',
    'victim_lat', 'victim_lon', 'beneficiary_bank_enc',
    'victim_district_enc', 'is_insider_case_enc',
    'hour', 'is_weekend_enc'
]

df['fraud_type_enc'] = le_fraud.transform(df['fraud_type'])
df['beneficiary_bank_enc'] = le_bank.transform(df['beneficiary_bank'])
df['victim_district_enc'] = le_district.transform(df['victim_district'])
df['is_insider_case_enc'] = df['is_insider_case'].astype(int)
df['is_weekend_enc'] = df['is_weekend'].astype(int)

X = df[feature_cols]

# ============================================================
# 2. TRAIN AN ANOMALY DETECTOR ON THE FEATURE SPACE
#    This directly answers "is this input weird compared to
#    everything we've seen?" — independent of the prediction model.
# ============================================================
print("Fitting anomaly detector on training feature space...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

iso_forest = IsolationForest(
    n_estimators=200,
    contamination=0.02,  # assume ~2% of training data itself looks "unusual"
    random_state=42,
    n_jobs=-1
)
iso_forest.fit(X_scaled)

joblib.dump(iso_forest, "models/anomaly_detector.pkl")
joblib.dump(scaler, "models/feature_scaler.pkl")
print("Anomaly detector saved to models/anomaly_detector.pkl")

# ============================================================
# 2b. RANGE BOUNDS — captured from training data, used as a
#     simple, explainable first-pass filter. Any feature value
#     outside these bounds is automatically flagged — no ML needed
#     for this part, and it's easy to explain in a demo.
# ============================================================
feature_ranges = {
    col: (float(X[col].min()), float(X[col].max())) for col in feature_cols
}
joblib.dump(feature_ranges, "models/feature_ranges.pkl")
print("\nFeature ranges captured from training data:")
for col, (lo, hi) in feature_ranges.items():
    print(f"  {col}: [{lo:.2f}, {hi:.2f}]")

def is_out_of_range(feature_row_df, ranges, tolerance=1.1):
    """Returns True if any feature is outside [min, max] * tolerance from training data."""
    row = feature_row_df.iloc[0]
    for col, (lo, hi) in ranges.items():
        margin = (hi - lo) * (tolerance - 1)
        if row[col] < lo - margin or row[col] > hi + margin:
            return True, col
    return False, None


def predict_with_confidence_gate(feature_row_df):
    """
    feature_row_df: single-row DataFrame with the model's feature columns
    (same columns/order as feature_cols).
    Returns prediction + confidence + gate decision.

    Gate fires (ANALYST_REVIEW) if EITHER:
      - any feature is outside the observed training range (explainable, reliable), OR
      - the isolation forest flags the overall combination as anomalous
    """
    pred = model.predict(feature_row_df)
    lat, lon = float(pred[0][0]), float(pred[0][1])

    out_of_range, which_feature = is_out_of_range(feature_row_df, feature_ranges)

    row_scaled = scaler.transform(feature_row_df)
    anomaly_score = float(iso_forest.decision_function(row_scaled)[0])
    is_anomaly = iso_forest.predict(row_scaled)[0] == -1

    confidence = float(np.clip((anomaly_score + 0.3) / 0.5, 0, 1))
    if out_of_range:
        confidence = min(confidence, 0.2)  # force low confidence if out of range

    flagged = out_of_range or is_anomaly
    reason = f"out-of-range: {which_feature}" if out_of_range else (
        "anomalous combination" if is_anomaly else "normal"
    )

    return {
        "predicted_lat": lat,
        "predicted_lon": lon,
        "anomaly_score": round(anomaly_score, 4),
        "confidence": round(confidence, 3),
        "reason": reason,
        "gate_decision": "ANALYST_REVIEW" if flagged else "AUTO_DISPATCH"
    }

# ============================================================
# 4. TEST ON THE SAME SAMPLE + OOD CASES — verify it actually discriminates
# ============================================================
print("\n" + "=" * 60)
print("IN-DISTRIBUTION SAMPLE TEST")
print("=" * 60)
sample_idx = np.random.choice(len(X), size=min(300, len(X)), replace=False)
sample_results = []
for idx in sample_idx:
    row_df = X.iloc[[idx]]
    result = predict_with_confidence_gate(row_df)
    sample_results.append(result)

sample_df = pd.DataFrame(sample_results)
print(sample_df['gate_decision'].value_counts())
print(f"Mean confidence: {sample_df['confidence'].mean():.3f}")

print("\n" + "=" * 60)
print("OUT-OF-DISTRIBUTION TEST CASES")
print("=" * 60)

ood_cases = [
    {
        "name": "Extreme amount (10x max seen)",
        "row": {'fraud_type_enc': 0, 'amount_lost': 50000000, 'number_of_hops': 5,
                'victim_lat': 22.5, 'victim_lon': 78.0, 'beneficiary_bank_enc': 0,
                'victim_district_enc': 0, 'is_insider_case_enc': 0, 'hour': 12, 'is_weekend_enc': 0}
    },
    {
        "name": "Extreme hops (way beyond max of 10)",
        "row": {'fraud_type_enc': 0, 'amount_lost': 50000, 'number_of_hops': 40,
                'victim_lat': 22.5, 'victim_lon': 78.0, 'beneficiary_bank_enc': 0,
                'victim_district_enc': 0, 'is_insider_case_enc': 0, 'hour': 12, 'is_weekend_enc': 0}
    },
    {
        "name": "Victim location far outside training range (e.g. Kashmir)",
        "row": {'fraud_type_enc': 0, 'amount_lost': 50000, 'number_of_hops': 3,
                'victim_lat': 34.0, 'victim_lon': 74.8, 'beneficiary_bank_enc': 0,
                'victim_district_enc': 0, 'is_insider_case_enc': 0, 'hour': 12, 'is_weekend_enc': 0}
    },
    {
        "name": "Normal in-distribution case (control — should NOT flag)",
        "row": {'fraud_type_enc': 0, 'amount_lost': 30000, 'number_of_hops': 3,
                'victim_lat': 22.5, 'victim_lon': 78.0, 'beneficiary_bank_enc': 0,
                'victim_district_enc': 0, 'is_insider_case_enc': 0, 'hour': 12, 'is_weekend_enc': 0}
    },
]

for case in ood_cases:
    row_df = pd.DataFrame([case["row"]])[feature_cols]
    result = predict_with_confidence_gate(row_df)
    print(f"\n{case['name']}:")
    print(f"  anomaly_score={result['anomaly_score']}  confidence={result['confidence']}  -> {result['gate_decision']}")