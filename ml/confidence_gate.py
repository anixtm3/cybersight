import pandas as pd
import numpy as np
import joblib
import json

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
# 2. CONFIDENCE = agreement across the XGBoost ensemble's trees
#    We use per-tree prediction variance as a proxy for confidence.
#    Low variance across trees = model is confident (in-distribution).
#    High variance = trees disagree = likely novel/out-of-distribution case.
# ============================================================
def get_tree_predictions(estimator, X_row):
    """Get predictions from each boosting round (staged) for one estimator."""
    booster = estimator.get_booster()
    dmatrix = xgb_module.DMatrix(X_row)
    # ntree_limit staged predictions to see how prediction evolves/stabilizes
    preds = []
    n_trees = booster.num_boosted_rounds()
    step = max(1, n_trees // 20)  # sample ~20 checkpoints across boosting rounds
    for i in range(step, n_trees + 1, step):
        p = booster.predict(dmatrix, iteration_range=(0, i))
        preds.append(p[0])
    return np.array(preds)

import xgboost as xgb_module

def compute_confidence(row_idx, X):
    """
    Returns a confidence score (0-1, higher = more confident) and
    the raw uncertainty (km) for one complaint's prediction.
    """
    X_row = X.iloc[[row_idx]]

    preds_lat = get_tree_predictions(model.estimators_[0], X_row)
    preds_lon = get_tree_predictions(model.estimators_[1], X_row)

    # How much does the prediction still move in the later boosting rounds?
    # Large late-stage movement = model is uncertain / still "arguing with itself"
    lat_std = np.std(preds_lat[-5:])  # std of last 5 checkpoints
    lon_std = np.std(preds_lon[-5:])

    # Convert degree-std to a rough km uncertainty measure
    uncertainty_km = np.sqrt(lat_std**2 + lon_std**2) * 111  # ~111km per degree

    # Map uncertainty to a 0-1 confidence score (tunable thresholds)
    # < 5km std -> high confidence, > 50km std -> low confidence
    confidence = float(np.clip(1 - (uncertainty_km / 50), 0, 1))

    return confidence, float(uncertainty_km)

# ============================================================
# 3. RUN ON A SAMPLE, FLAG LOW-CONFIDENCE (NOVEL PATTERN) CASES
# ============================================================
print("Computing confidence scores on a sample...")
sample_idx = np.random.choice(len(X), size=min(300, len(X)), replace=False)

results = []
for idx in sample_idx:
    conf, unc_km = compute_confidence(idx, X)
    results.append({
        "row_index": int(idx),
        "confidence": round(conf, 3),
        "uncertainty_km": round(unc_km, 2),
        "flag": "ANALYST REVIEW" if conf < 0.4 else "AUTO-DISPATCH OK"
    })

results_df = pd.DataFrame(results)

print("\n" + "=" * 60)
print("CONFIDENCE GATE SUMMARY")
print("=" * 60)
print(results_df['flag'].value_counts())
print(f"\nMean confidence: {results_df['confidence'].mean():.3f}")
print(f"Flagged for review: {(results_df['flag']=='ANALYST REVIEW').sum()} / {len(results_df)}")

print("\nLowest-confidence example (most 'novel' case in sample):")
lowest = results_df.sort_values('confidence').iloc[0]
print(json.dumps(lowest.to_dict(), indent=2))

# ============================================================
# 4. FUNCTION FOR SINGLE-COMPLAINT USE (what Kartike's API calls)
# ============================================================
def predict_with_confidence_gate(feature_row_df):
    """
    feature_row_df: single-row DataFrame with the model's feature columns.
    Returns prediction + confidence + gate decision — this is the
    documented interface Kartike's ingest endpoint should call.
    """
    pred = model.predict(feature_row_df)
    lat, lon = float(pred[0][0]), float(pred[0][1])

    # reuse confidence logic on this single row
    preds_lat = get_tree_predictions(model.estimators_[0], feature_row_df)
    preds_lon = get_tree_predictions(model.estimators_[1], feature_row_df)
    lat_std = np.std(preds_lat[-5:])
    lon_std = np.std(preds_lon[-5:])
    uncertainty_km = np.sqrt(lat_std**2 + lon_std**2) * 111
    confidence = float(np.clip(1 - (uncertainty_km / 50), 0, 1))

    return {
        "predicted_lat": lat,
        "predicted_lon": lon,
        "confidence": round(confidence, 3),
        "uncertainty_km": round(float(uncertainty_km), 2),
        "gate_decision": "ANALYST_REVIEW" if confidence < 0.4 else "AUTO_DISPATCH"
    }

# Save results sample for the team to inspect
results_df.to_csv("models/confidence_gate_sample.csv", index=False)
print("\nSaved sample results to models/confidence_gate_sample.csv")

# ============================================================
# 5. REAL TEST — genuinely out-of-distribution cases
#    (training sample above was all in-distribution, so it told us
#    nothing about whether the gate actually fires. This does.)
# ============================================================
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
    print(f"  confidence={result['confidence']}  uncertainty_km={result['uncertainty_km']}  -> {result['gate_decision']}")