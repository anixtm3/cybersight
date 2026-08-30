# CyberSight AI — ML Module
**Project:** PS 26184 | MHA / I4C | SIH 2026  
**Team:** INNOVAULT | ABESIT Ghaziabad  
**Engineer:** Saina Sharma  
**Branch:** `saina-ml`

---

## Overview

XGBoost-based district classifier that predicts the most likely cash withdrawal district from cybercrime complaint features, then ranks Top 5 ATMs within that district using PostGIS-backed ATM data.

**Approach:** District Classification → PostGIS ATM Ranking  
**Not used:** Direct coordinate regression (too noisy on synthetic data)

---

## Model Performance

| Metric | Value |
|--------|-------|
| Naive baseline (always predict Delhi NCR) | 26.9% |
| Top-1 Accuracy | **90.0%** |
| Top-3 Accuracy | **100.0%** |
| Top-5 Accuracy | **100.0%** |
| Improvement over baseline | **+63.1 percentage points** |
| Inference time | **9.76 ms** |
| End-to-end SLA | 60 seconds |

---

## Setup

### Requirements
```bash
.venv\Scripts\pip install -r ML/requirements.txt
```

### Environment
Create `DB/.env`:
DB_PASSWORD=your_password_here


### Train Model
```bash
.venv\Scripts\python ML\train_model.py
```

---

## Model Architecture

### Input — 19 Features (exact order critical)

| # | Feature | Type | Source |
|---|---------|------|--------|
| 1 | `fraud_type_enc` | int | `le_fraud.transform([fraud_type])` |
| 2 | `amount_lost` | float | raw complaint value |
| 3 | `number_of_hops` | int | raw complaint value |
| 4 | `victim_lat` | float | raw complaint value |
| 5 | `victim_lon` | float | raw complaint value |
| 6 | `bank_enc` | int | `le_bank.transform([beneficiary_bank])` |
| 7 | `account_age_days` | int | default 180 at inference |
| 8 | `mule_network_flag` | int | 1 if number_of_hops >= 4 else 0 |
| 9 | `is_festival_period` | int | hardcode 0 at inference |
| 10 | `hour_of_day_sin` | float | sin(2π × hour / 24) |
| 11 | `hour_of_day_cos` | float | cos(2π × hour / 24) |
| 12 | `day_of_week` | int | 0=Monday, 6=Sunday |
| 13 | `is_weekend` | int | 1 if day_of_week >= 5 else 0 |
| 14 | `rolling_6h_complaint_count` | int | DB query — same district last 6h |
| 15 | `district_risk_score` | float | DB query — AVG per victim_district |
| 16 | `atm_density` | int | PostGIS — ATMs within 5km of victim coords |
| 17 | `time_since_last_complaint_same_bank` | float | DB query — hours, -1 if none |
| 18 | `victim_to_withdrawal_distance_km` | float | hardcode 0.0 at inference |
| 19 | `district_enc` | int | `le_district.transform([victim_district])` |

### Output
```python
predicted_district = le_target.inverse_transform([pred])[0]  # e.g. "Delhi NCR"
```

### Top 5 ATMs
```python
atm_df = pkg['atm_df']
top5 = atm_df[atm_df['district'] == predicted_district].head(5)
# columns: atm_id, district, bank_name, lon, lat
```

---

## model.pkl Structure

```python
import pickle
with open('ML/model.pkl', 'rb') as f:
    pkg = pickle.load(f)

# Keys:
# pkg['model']                   — XGBClassifier
# pkg['features']                — list of 19 feature names in order
# pkg['le_fraud']                — LabelEncoder for fraud_type
# pkg['le_bank']                 — LabelEncoder for beneficiary_bank
# pkg['le_district']             — LabelEncoder for victim_district (INPUT)
# pkg['le_target']               — LabelEncoder for withdrawal_district (OUTPUT)
# pkg['top1_accuracy']           — 0.90
# pkg['top3_accuracy']           — 1.00
# pkg['top5_accuracy']           — 1.00
# pkg['naive_baseline']          — 0.269
# pkg['naive_baseline_district'] — 'Delhi NCR'
# pkg['shap_importance']         — dict of feature: mean_shap_value
# pkg['atm_df']                  — DataFrame with atm_id, district, bank_name, lon, lat
# pkg['district_classes']        — list of 10 district names
```

---

## Integration — Kartike ke liye

### Load (once at startup)
```python
import pickle
with open('ML/model.pkl', 'rb') as f:
    MODEL_PKG = pickle.load(f)
```

### Encode Input
```python
fraud_type_enc = int(MODEL_PKG['le_fraud'].transform([fraud_type])[0])
bank_enc       = int(MODEL_PKG['le_bank'].transform([beneficiary_bank])[0])
district_enc   = int(MODEL_PKG['le_district'].transform([victim_district])[0])
```

### Predict
```python
import pandas as pd

X = pd.DataFrame([input_dict])[MODEL_PKG['features']]
proba = MODEL_PKG['model'].predict_proba(X)[0]
confidence = float(max(proba))
pred_enc = proba.argmax()
predicted_district = MODEL_PKG['le_target'].inverse_transform([pred_enc])[0]

# Novel pattern gate
novel_pattern = confidence < 0.4

# Top 5 ATMs
atm_df = MODEL_PKG['atm_df']
top5 = atm_df[atm_df['district'] == predicted_district].head(5)

# Freezable amount
freezable_amount = round(amount_lost * 0.6, 2)
```

### Response Shape
```python
{
    "predicted_district":        str,    # e.g. "Delhi NCR"
    "confidence":                float,  # 0.0 - 1.0
    "novel_pattern":             bool,   # True if confidence < 0.4
    "risk_level":                str,    # "HIGH"/"MEDIUM"/"LOW"
    "freezable_amount":          float,  # amount_lost * 0.6
    "withdrawal_window_minutes": int,    # 45 default
    "top_5_atms": [
        {
            "atm_id":    str,
            "bank_name": str,
            "lat":       float,
            "lon":       float,
            "district":  str
        }
    ],
    "shap_values": dict
}
```

---

## SHAP — Top Features

| Rank | Feature | Mean SHAP |
|------|---------|------|
| 1 | victim_lat | 2.883 |
| 2 | victim_lon | 2.174 |
| 3 | district_enc | 0.864 |
| 4 | victim_to_withdrawal_distance_km | 0.767 |
| 5 | district_risk_score | 0.530 |

---

## Districts Covered

Delhi, Delhi NCR, Mumbai, Jamtara, Bengaluru, Hyderabad, Agra, Patna, Pune, Lucknow

---

## Q&A — Anticipated Judge Questions

**"24h rolling window kahan hai?"**
6h window already implement hai jo short burst patterns detect karta hai — fraud cash withdrawal 30-120 min mein hoti hai, isliye 6h zyada relevant hai. 24h window production mein add karenge.

**"Synthetic data pe trained model real world mein kaise kaam karega?"**
Architecture validate karna prototype ka goal hai. Synthetic data NCRB/I4C typologies pe based hai. Real data pe retraining production deployment pe hogi — architecture unchanged rahega.

**"Model galat predict kare to?"**
Output ranked probability distribution hai — single assertion nahi. SHAP values har prediction ke saath hain — investigator evaluate aur reject kar sakta hai. Low confidence pe ANALYST_REVIEW flag hota hai, auto-dispatch suppress hota hai.

---

## Data Statement

Synthetic dataset — NCRB/I4C published fraud typologies se derived. No real PII. Production deployment requires retraining on authorised I4C data under MoU.