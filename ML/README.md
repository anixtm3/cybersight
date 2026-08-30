# CyberSight — ML Model (Saina)

**Branch:** `saina-ml`  
**Stack:** XGBoost, SHAP, scikit-learn, GeoPandas, pandas, Python 3.11

---

## What I Built

### Approach

XGBoost district classifier → PostGIS Top-5 ATM ranking

Two approaches were evaluated:
- **Option A:** Direct withdrawal coordinate regression → 75km MAE (rejected — withdrawal coords were randomly generated, no learnable signal)
- **Option B (chosen):** Predict withdrawal district → rank Top-5 ATMs from that district via `atm_df`

### Results

| Metric | Value |
|--------|-------|
| Naive baseline | 26.9% (always predict Delhi NCR) |
| Top-1 Accuracy | 90.0% |
| Top-3 Accuracy | 100.0% |
| Top-5 Accuracy | 100.0% |
| Improvement over baseline | +63.1 percentage points |
| Inference time | 9.76 ms |

### 19 Features (exact training order)

```
fraud_type_enc, amount_lost, number_of_hops,
victim_lat, victim_lon, bank_enc, account_age_days,
mule_network_flag, is_festival_period, hour_of_day_sin,
hour_of_day_cos, day_of_week, is_weekend,
rolling_6h_complaint_count, district_risk_score,
atm_density, time_since_last_complaint_same_bank,
victim_to_withdrawal_distance_km, district_enc
```

### `model.pkl` Contents

| Key | Description |
|-----|-------------|
| `model` | XGBClassifier |
| `features` | 19-feature list in exact order |
| `le_fraud` | Input encoder — fraud type |
| `le_bank` | Input encoder — bank name |
| `le_district` | Input encoder — victim district **(INPUT only)** |
| `le_target` | Output decoder — predicted withdrawal district **(OUTPUT only)** |
| `atm_df` | DataFrame: `atm_id, district, bank_name, lon, lat` |
| `naive_baseline` | 0.269 |
| `shap_importance` | Feature importance dict |
| `district_classes` | All district labels |

**Critical distinction:** `le_district` encodes the INPUT feature `district_enc`. `le_target` decodes the OUTPUT predicted district. These must never be mixed.

### Inference-Time Feature Decisions

| Feature | Value at Inference | Reason |
|---------|-------------------|--------|
| `account_age_days` | 180 (default) | Not available at complaint time |
| `mule_network_flag` | 1 if hops ≥ 4 else 0 | Derived from complaint |
| `is_festival_period` | 0 (hardcoded) | Festival dates are 2024-only; demo is 2026 |
| `atm_density` | PostGIS query on victim coords | Withdrawal coords are prediction target — circular dependency |
| `district_risk_score` | DB query, parameterized | AVG from complaints table |
| `time_since_last_complaint_same_bank` | DB query, -1 if none | Hours since last complaint, same bank |
| `victim_to_withdrawal_distance_km` | 0.0 | Unknown at inference time |

### Novel Pattern Gate

- Confidence < 0.4 → `ANALYST_REVIEW` status returned
- Auto-dispatch suppressed
- Prediction still logged for analyst review

### SHAP

- `TreeExplainer` used per prediction
- Output: dict of `{feature: shap_value}` — JSON-serialisable
- Signs interpretable — positive = increases risk, negative = decreases
- Stored in `predictions.shap_values` as JSONB

---

## Verified

- Model loads and predicts on fresh Python process ✅
- Beats naive baseline by 63.1 pp ✅
- Top-3 and Top-5 accuracy: 100% ✅
- SHAP values JSON-serialisable, signs correct ✅
- Inference latency 9.76ms — well under 60s budget ✅
- End-to-end: `TEST-LIVE-003` → `DEL00001`, `HIGH`, confidence 0.891 ✅
- `atm_df` columns confirmed: `atm_id, district, bank_name, lon, lat` ✅

---

## Setup

```bash
cd ML
pip install -r requirements.txt
python train_model.py
```

**model.pkl location:** Place at `ML/model.pkl` — repo root level, outside `backend/`. Kartike's `predict.py` resolves path as `../../ML/model.pkl` relative to `backend/app/models/`.

---

## Q&A Prep

**"24h rolling window?"**
6h window used — fraud cash-out happens within 30–120 minutes of complaint. 24h is production roadmap item.

**"Synthetic data?"**
Architecture feasibility demo based on NCRB typologies. Model clearly beats naive baseline on causal structure in data. Real data retraining on authorised NCRP feeds is the defined next step — architecture unchanged.

**"Wrong prediction?"**
Output is a ranked probability distribution, not a single assertion. Every prediction carries SHAP reasoning an investigator can inspect and reject. Confidence < 0.4 suppresses auto-dispatch entirely.

**"Why XGBoost?"**
Fast inference (9.76ms), handles mixed feature types, native SHAP support via TreeExplainer, production-proven on tabular fraud data.