import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.multioutput import MultiOutputRegressor
import joblib

# ============================================================
# 1. LOAD ENGINEERED DATA
# ============================================================
df = pd.read_csv("data/complaints_engineered.csv")
df['complaint_datetime'] = pd.to_datetime(df['complaint_datetime'])

print(f"Loaded {len(df)} rows")

# ============================================================
# 2. HAVERSINE HELPER (same as Day 1 — needed for evaluation)
# ============================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

# ============================================================
# 3. ENCODE CATEGORICAL FEATURES
# ============================================================
le_fraud = LabelEncoder()
le_bank = LabelEncoder()
le_district = LabelEncoder()

df['fraud_type_enc'] = le_fraud.fit_transform(df['fraud_type'])
df['beneficiary_bank_enc'] = le_bank.fit_transform(df['beneficiary_bank'])
df['victim_district_enc'] = le_district.fit_transform(df['victim_district'])
df['is_insider_case_enc'] = df['is_insider_case'].astype(int)
df['is_weekend_enc'] = df['is_weekend'].astype(int)

# ============================================================
# 4. FEATURES AND TARGETS
# ============================================================
feature_cols = [
    'fraud_type_enc', 'amount_lost', 'number_of_hops',
    'victim_lat', 'victim_lon', 'beneficiary_bank_enc',
    'victim_district_enc', 'is_insider_case_enc',
    'hour', 'is_weekend_enc'
]

X = df[feature_cols]
y = df[['withdrawal_lat', 'withdrawal_lon']]  # regress directly on coordinates

# Keep victim coords + zone alongside for evaluation after split
aux = df[['victim_lat', 'victim_lon', 'withdrawal_zone']]

X_train, X_test, y_train, y_test, aux_train, aux_test = train_test_split(
    X, y, aux, test_size=0.2, random_state=42
)

print(f"Train: {len(X_train)}  Test: {len(X_test)}")

# ============================================================
# 5. TRAIN MODEL — separate XGBoost regressor per coordinate
# ============================================================
model = MultiOutputRegressor(
    xgb.XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
)

print("\nTraining model...")
model.fit(X_train, y_train)
print("Training complete.")

# ============================================================
# 6. PREDICT AND EVALUATE — displacement error (the metric that matters)
# ============================================================
y_pred = model.predict(X_test)
pred_lat, pred_lon = y_pred[:, 0], y_pred[:, 1]
actual_lat, actual_lon = y_test['withdrawal_lat'].values, y_test['withdrawal_lon'].values

displacement_error_km = haversine(pred_lat, pred_lon, actual_lat, actual_lon)

mean_error = displacement_error_km.mean()
median_error = np.median(displacement_error_km)

print("\n" + "=" * 60)
print("MODEL PERFORMANCE vs DAY 1 BASELINE")
print("=" * 60)
print(f"{'Metric':<30}{'Baseline':>15}{'Model':>15}")
print(f"{'Mean displacement error':<30}{'707.61 km':>15}{f'{mean_error:.2f} km':>15}")
print(f"{'Median displacement error':<30}{'644.34 km':>15}{f'{median_error:.2f} km':>15}")

improvement = (1 - mean_error / 707.61) * 100
print(f"\nImprovement over baseline: {improvement:.1f}%")

if mean_error < 707.61 * 0.5:
    print("STATUS: Model is learning real signal. Clear improvement over baseline.")
elif mean_error < 707.61 * 0.85:
    print("STATUS: Marginal improvement. Investigate features / hyperparameters before trusting this.")
else:
    print("STATUS: WARNING — barely beats baseline. Treat as REBUILD candidate.")

# ============================================================
# 7. TOP-K ACCURACY (proxy) — nearest actual zones to the prediction
# ============================================================
# Build a lookup of unique zone centroids from training data
zone_centroids = df.groupby('withdrawal_zone')[['withdrawal_lat', 'withdrawal_lon']].mean()

def top_k_zone_accuracy(pred_lat, pred_lon, true_zone, k):
    hits = 0
    zone_coords = zone_centroids[['withdrawal_lat', 'withdrawal_lon']].values
    zone_names = zone_centroids.index.values
    for plat, plon, tz in zip(pred_lat, pred_lon, true_zone):
        dists = haversine(plat, plon, zone_coords[:, 0], zone_coords[:, 1])
        nearest_idx = np.argsort(dists)[:k]
        nearest_zones = zone_names[nearest_idx]
        if tz in nearest_zones:
            hits += 1
    return hits / len(true_zone)

print("\n" + "=" * 60)
print("TOP-K ZONE ACCURACY (nearest predicted zones vs true zone)")
print("=" * 60)
# Use a sample for speed if test set is large
sample_size = min(2000, len(aux_test))
sample_idx = np.random.choice(len(aux_test), sample_size, replace=False)

for k in [1, 5, 10]:
    acc = top_k_zone_accuracy(
        pred_lat[sample_idx], pred_lon[sample_idx],
        aux_test['withdrawal_zone'].values[sample_idx], k
    )
    baseline_acc = {1: 0.0033, 5: 0.0160, 10: 0.0315}[k]
    print(f"Top-{k}: model={acc:.4f}  baseline={baseline_acc:.4f}")

# ============================================================
# 8. SAVE MODEL + ENCODERS
# ============================================================
joblib.dump(model, "models/withdrawal_predictor.pkl")
joblib.dump(le_fraud, "models/le_fraud.pkl")
joblib.dump(le_bank, "models/le_bank.pkl")
joblib.dump(le_district, "models/le_district.pkl")
zone_centroids.to_csv("models/zone_centroids.csv")

print("\nModel and encoders saved to models/")