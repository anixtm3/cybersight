import pandas as pd
import numpy as np

# ============================================================
# 1. LOAD DATA
# ============================================================
df = pd.read_csv("data/synthetic_complaints_v2.csv")
df['complaint_datetime'] = pd.to_datetime(df['complaint_datetime'])

# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

# Discretize withdrawal location into zones (~5km grid cells)
df['withdrawal_zone'] = (
    df['withdrawal_lat'].round(1).astype(str) + "_" +
    df['withdrawal_lon'].round(1).astype(str)
)

# Freezable amount — heuristic: fewer hops = more freezable,
# insider cases = highly freezable (money hasn't moved far)
df['freezable_amount'] = df['amount_lost'] * np.clip(
    1 - (df['number_of_hops'] - 1) * 0.15, 0.1, 1.0
)
df.loc[df['is_insider_case'] == True, 'freezable_amount'] = df['amount_lost'] * 0.9

# Temporal features (currently weak signal in the data — low priority,
# keep them in the schema but don't expect much predictive value yet)
df['hour'] = df['complaint_datetime'].dt.hour
df['is_weekend'] = df['complaint_datetime'].dt.weekday >= 5

# Drop constant/useless columns
if 'status' in df.columns and df['status'].nunique() == 1:
    df = df.drop(columns=['status'])

# ============================================================
# 3. HAVERSINE DISTANCE HELPER (km)
# ============================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

df['displacement_km'] = haversine(
    df['victim_lat'], df['victim_lon'],
    df['withdrawal_lat'], df['withdrawal_lon']
)

# ============================================================
# 4. SAVE ENGINEERED DATASET
# ============================================================
df.to_csv("data/complaints_engineered.csv", index=False)

print("=" * 60)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 60)
print("Shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nSample:\n", df[['withdrawal_zone', 'freezable_amount', 'is_insider_case', 'alert_level']].head())

# ============================================================
# 5. BASELINE METRICS — the ones that actually matter
# ============================================================
print("\n" + "=" * 60)
print("BASELINE METRICS (for tomorrow's model to beat)")
print("=" * 60)

# --- WRONG metric, kept only for reference: plain zone-match accuracy ---
most_common_zone = df['withdrawal_zone'].mode()[0]
naive_zone_accuracy = (df['withdrawal_zone'] == most_common_zone).mean()
print(f"\n[Reference only — NOT the real metric]")
print(f"Naive 'most common zone' accuracy: {naive_zone_accuracy:.4f}")
print(f"Number of unique zones: {df['withdrawal_zone'].nunique()}")
print("(This metric is misleading with 7000+ classes — nearly any model")
print(" will 'beat' it trivially. Do not report this as the baseline.)")

# --- RIGHT metric #1: mean/median displacement error (km) ---
mean_lat, mean_lon = df['withdrawal_lat'].mean(), df['withdrawal_lon'].mean()
df['baseline_error_km'] = haversine(
    df['withdrawal_lat'], df['withdrawal_lon'], mean_lat, mean_lon
)
print(f"\n[REAL baseline #1 — mean displacement error]")
print(f"Naive baseline (always predict mean location):")
print(f"  Mean displacement error:   {df['baseline_error_km'].mean():.2f} km")
print(f"  Median displacement error: {df['baseline_error_km'].median():.2f} km")

# --- RIGHT metric #2: top-k accuracy baseline ---
# Naive top-k baseline: the k most frequent zones overall.
# A real model should beat this using a per-complaint ranked list of
# candidate zones (e.g. predicted probability distribution).
for k in [1, 5, 10]:
    top_k_zones = df['withdrawal_zone'].value_counts().head(k).index
    top_k_accuracy = df['withdrawal_zone'].isin(top_k_zones).mean()
    print(f"  Naive top-{k} accuracy (most frequent {k} zones): {top_k_accuracy:.4f}")

print("\n" + "=" * 60)
print("Tomorrow's model must clearly beat the displacement error")
print("and top-k accuracy baselines above — not the naive zone-match number.")
print("=" * 60)