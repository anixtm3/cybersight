import os
import numpy as np
import pandas as pd
import psycopg2
import pickle
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from xgboost import XGBClassifier
import shap
import warnings
warnings.filterwarnings('ignore')

load_dotenv(dotenv_path='DB/.env')

conn = psycopg2.connect(
    dbname="cybersight",
    user="postgres",
    password=os.environ.get("DB_PASSWORD", ""),
    host="localhost",
    port="5433"
)

print("Loading data from DB...")
query = """
    SELECT 
        fraud_type, amount_lost, number_of_hops,
        victim_lat, victim_lon,
        beneficiary_bank,
        account_age_days, mule_network_flag,
        is_festival_period, hour_of_day_sin, hour_of_day_cos,
        day_of_week, is_weekend,
        rolling_6h_complaint_count, district_risk_score,
        atm_density, time_since_last_complaint_same_bank,
        victim_to_withdrawal_distance_km,
        victim_district,
        target_atm_id,
        withdrawal_lat, withdrawal_lon
    FROM complaints
    WHERE target_atm_id IS NOT NULL
"""
df = pd.read_sql(query, conn)
print(f"Loaded {len(df)} rows")

print("Loading ATM district mapping...")
atm_query = """
    SELECT atm_id, district, 
           ST_X(location::geometry) as lon,
           ST_Y(location::geometry) as lat
    FROM atm_locations
"""
atm_df = pd.read_sql(atm_query, conn)
atm_district_map = dict(zip(atm_df['atm_id'], atm_df['district']))

df['withdrawal_district'] = df['target_atm_id'].map(atm_district_map)
df = df.dropna(subset=['withdrawal_district'])
print(f"After district mapping: {len(df)} rows")
print(f"Withdrawal district distribution:\n{df['withdrawal_district'].value_counts()}")

print("\nPreparing features...")

le_fraud    = LabelEncoder()
le_bank     = LabelEncoder()
le_district = LabelEncoder()
le_target   = LabelEncoder()

df['fraud_type_enc']      = le_fraud.fit_transform(df['fraud_type'])
df['bank_enc']            = le_bank.fit_transform(df['beneficiary_bank'])
df['district_enc']        = le_district.fit_transform(df['victim_district'])
df['withdrawal_dist_enc'] = le_target.fit_transform(df['withdrawal_district'])

df['mule_network_flag']   = df['mule_network_flag'].astype(int)
df['is_festival_period']  = df['is_festival_period'].astype(int)
df['is_weekend']          = df['is_weekend'].astype(int)
df['time_since_last_complaint_same_bank'] = df['time_since_last_complaint_same_bank'].fillna(-1)
df['rolling_6h_complaint_count']          = df['rolling_6h_complaint_count'].fillna(0)

FEATURES = [
    'fraud_type_enc', 'amount_lost', 'number_of_hops',
    'victim_lat', 'victim_lon',
    'bank_enc', 'account_age_days', 'mule_network_flag',
    'is_festival_period', 'hour_of_day_sin', 'hour_of_day_cos',
    'day_of_week', 'is_weekend',
    'rolling_6h_complaint_count', 'district_risk_score',
    'atm_density', 'time_since_last_complaint_same_bank',
    'victim_to_withdrawal_distance_km', 'district_enc'
]

X = df[FEATURES]
y = df['withdrawal_dist_enc']

n_classes = len(le_target.classes_)
print(f"Classes (withdrawal districts): {n_classes}")
print(f"Districts: {list(le_target.classes_)}")

# Naive baseline
most_common_district = df['withdrawal_district'].value_counts().index[0]
naive_baseline = df['withdrawal_district'].value_counts().iloc[0] / len(df)
print(f"\nNaive baseline (always predict '{most_common_district}'): {naive_baseline*100:.1f}%")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

print("\nTraining XGBoost classifier...")
model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist',
    device='cpu',
    n_jobs=-1,
    num_class=n_classes,
    objective='multi:softprob',
    eval_metric='mlogloss'
)
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=50
)

y_pred       = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

top1_acc = accuracy_score(y_test, y_pred)
top3_acc = top_k_accuracy_score(y_test, y_pred_proba, k=3)
top5_acc = top_k_accuracy_score(y_test, y_pred_proba, k=5)

print(f"\n── Evaluation ──")
print(f"Naive baseline:  {naive_baseline*100:.1f}%")
print(f"Top-1 Accuracy:  {top1_acc*100:.1f}%")
print(f"Top-3 Accuracy:  {top3_acc*100:.1f}%")
print(f"Top-5 Accuracy:  {top5_acc*100:.1f}%")
print(f"Improvement:     +{(top1_acc - naive_baseline)*100:.1f} percentage points")

print("\nComputing SHAP values (sample 300 rows)...")
explainer   = shap.TreeExplainer(model)
shap_sample = X_test.sample(300, random_state=42)
shap_values = explainer.shap_values(shap_sample)

shap_array = np.array(shap_values)
print(f"SHAP array shape: {shap_array.shape}")

if shap_array.ndim == 3:
    if shap_array.shape[2] == n_classes:
        mean_shap = np.abs(shap_array).mean(axis=0).mean(axis=1)
    elif shap_array.shape[0] == n_classes:
        mean_shap = np.abs(shap_array).mean(axis=0).mean(axis=0)
    else:
        mean_shap = np.abs(shap_array).mean(axis=0).mean(axis=0)
else:
    mean_shap = np.abs(shap_array).mean(axis=0)

shap_importance = pd.Series(mean_shap, index=FEATURES).sort_values(ascending=False)
print("\nTop 10 important features (SHAP):")
print(shap_importance.head(10))

print("\nSaving model...")
model_package = {
    'model':                    model,
    'features':                 FEATURES,
    'le_fraud':                 le_fraud,
    'le_bank':                  le_bank,
    'le_district':              le_district,
    'le_target':                le_target,
    'top1_accuracy':            top1_acc,
    'top3_accuracy':            top3_acc,
    'top5_accuracy':            top5_acc,
    'naive_baseline':           naive_baseline,
    'naive_baseline_district':  most_common_district,
    'shap_importance':          shap_importance.to_dict(),
    'atm_df':                   atm_df,
    'district_classes':         list(le_target.classes_)
}

with open('ML/model.pkl', 'wb') as f:
    pickle.dump(model_package, f)

print("✅ Model saved to ML/model.pkl")
print(f"\n── Final Results ──")
print(f"Naive baseline:  {naive_baseline*100:.1f}%")
print(f"Top-1:  {top1_acc*100:.1f}% | Top-3: {top3_acc*100:.1f}% | Top-5: {top5_acc*100:.1f}%")
print(f"Improvement: +{(top1_acc - naive_baseline)*100:.1f} pp over naive baseline")

conn.close()