import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("data/synthetic_complaints_v2.csv")
df['complaint_datetime'] = pd.to_datetime(df['complaint_datetime'])

# 1. Discretize withdrawal location into zones (~5km grid cells)
df['withdrawal_zone'] = (
    df['withdrawal_lat'].round(1).astype(str) + "_" + 
    df['withdrawal_lon'].round(1).astype(str)
)

# 2. Freezable amount — heuristic: fewer hops = more freezable, insider cases = highly freezable
df['freezable_amount'] = df['amount_lost'] * np.clip(
    1 - (df['number_of_hops'] - 1) * 0.15, 0.1, 1.0
)
df.loc[df['is_insider_case'] == True, 'freezable_amount'] = df['amount_lost'] * 0.9

# 3. Temporal features (low predictive value currently, but structure should exist)
df['hour'] = df['complaint_datetime'].dt.hour
df['is_weekend'] = df['complaint_datetime'].dt.weekday >= 5

# Drop useless constant column
if df['status'].nunique() == 1:
    df = df.drop(columns=['status'])

# Save engineered dataset
df.to_csv("data/complaints_engineered.csv", index=False)

print("Shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nSample:\n", df[['withdrawal_zone', 'freezable_amount', 'is_insider_case', 'alert_level']].head())

# Baseline: naive "always predict most common zone"
most_common_zone = df['withdrawal_zone'].mode()[0]
baseline_accuracy = (df['withdrawal_zone'] == most_common_zone).mean()
print(f"\nNaive baseline accuracy: {baseline_accuracy:.4f}")
print(f"Number of unique zones: {df['withdrawal_zone'].nunique()}")