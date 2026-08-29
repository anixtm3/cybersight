import pandas as pd
import numpy as np
import shap
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
# 2. BUILD SHAP EXPLAINER — one per output (lat, lon)
#    model.estimators_[0] = lat regressor, [1] = lon regressor
# ============================================================
print("Building SHAP explainers...")
explainer_lat = shap.TreeExplainer(model.estimators_[0])
explainer_lon = shap.TreeExplainer(model.estimators_[1])

# Use a sample for speed — SHAP on full 50k rows is slow
sample = X.sample(n=min(500, len(X)), random_state=42)

shap_values_lat = explainer_lat.shap_values(sample)
shap_values_lon = explainer_lon.shap_values(sample)

print("SHAP values computed.")

# ============================================================
# 3. FUNCTION: explain a single complaint prediction as JSON
#    (this is what Kartike's ingest endpoint will call)
# ============================================================
def explain_prediction(row_idx, sample, shap_lat, shap_lon, feature_names):
    """Returns a JSON-serializable explanation for one prediction."""
    row_shap_lat = shap_lat[row_idx]
    row_shap_lon = shap_lon[row_idx]

    # combine lat/lon SHAP magnitude to get overall feature importance for this case
    combined_importance = np.abs(row_shap_lat) + np.abs(row_shap_lon)

    explanation = []
    for i, fname in enumerate(feature_names):
        explanation.append({
            "feature": fname,
            "shap_impact_lat": round(float(row_shap_lat[i]), 4),
            "shap_impact_lon": round(float(row_shap_lon[i]), 4),
            "combined_importance": round(float(combined_importance[i]), 4)
        })

    # sort by combined importance, descending
    explanation.sort(key=lambda x: x["combined_importance"], reverse=True)
    return explanation

# ============================================================
# 4. GLOBAL FEATURE IMPORTANCE — which features matter most overall
# ============================================================
mean_abs_shap_lat = np.abs(shap_values_lat).mean(axis=0)
mean_abs_shap_lon = np.abs(shap_values_lon).mean(axis=0)
combined_global = mean_abs_shap_lat + mean_abs_shap_lon

global_importance = sorted(
    zip(feature_cols, combined_global),
    key=lambda x: x[1], reverse=True
)

print("\n" + "=" * 60)
print("GLOBAL FEATURE IMPORTANCE (SHAP, averaged across sample)")
print("=" * 60)
for fname, imp in global_importance:
    print(f"{fname:<25} {imp:.4f}")

# ============================================================
# 5. EXAMPLE: explain ONE prediction (row 0 of the sample)
#    This is the JSON shape Kartike/Himanshu should expect
# ============================================================
example_explanation = explain_prediction(0, sample, shap_values_lat, shap_values_lon, feature_cols)

print("\n" + "=" * 60)
print("EXAMPLE PER-COMPLAINT EXPLANATION (JSON shape for API)")
print("=" * 60)
print(json.dumps(example_explanation, indent=2))

# ============================================================
# 6. SAVE example output to file so Kartike/Himanshu can see the schema
# ============================================================
with open("models/example_shap_output.json", "w") as f:
    json.dump(example_explanation, f, indent=2)

print("\nExample SHAP output saved to models/example_shap_output.json")
print("Share this file with Kartike and Himanshu — this is the JSON shape")
print("the predict interface will return alongside each prediction.")