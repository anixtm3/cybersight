import os
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = psycopg2.connect(
    dbname="cybersight",
    user="postgres",
    password=os.environ.get("DB_PASSWORD", ""),
    host="localhost",
    port="5433"
)
cur = conn.cursor()

# Causal rules
FRAUD_TYPE_CONFIG = {
    'UPI Fraud':         {'hop_min': 2, 'hop_max': 4, 'amount_mean': 8,  'amount_std': 1.2, 'displacement_factor': 1.0},
    'OLX Scam':          {'hop_min': 1, 'hop_max': 3, 'amount_mean': 9,  'amount_std': 1.0, 'displacement_factor': 0.8},
    'Investment Scam':   {'hop_min': 4, 'hop_max': 7, 'amount_mean': 11, 'amount_std': 1.5, 'displacement_factor': 2.0},
    'Romance Scam':      {'hop_min': 3, 'hop_max': 6, 'amount_mean': 10, 'amount_std': 1.3, 'displacement_factor': 1.8},
    'KYC Fraud':         {'hop_min': 2, 'hop_max': 4, 'amount_mean': 7,  'amount_std': 1.0, 'displacement_factor': 1.0},
    'Job Fraud':         {'hop_min': 1, 'hop_max': 3, 'amount_mean': 7,  'amount_std': 0.9, 'displacement_factor': 0.7},
    'Lottery Fraud':     {'hop_min': 2, 'hop_max': 5, 'amount_mean': 9,  'amount_std': 1.1, 'displacement_factor': 1.2},
    'Tech Support Fraud':{'hop_min': 1, 'hop_max': 3, 'amount_mean': 8,  'amount_std': 1.0, 'displacement_factor': 0.6},
}

BANKS = ['SBI', 'HDFC', 'ICICI', 'Axis', 'PNB', 'Kotak', 'BOB', 'Canara']

# Fix 1 — Bank corridor: har bank ka preferred direction (degrees) aur reach (km multiplier)
BANK_CONFIG = {
    'SBI':    {'preferred_bearing': 45,  'reach_factor': 1.2},  # Northeast
    'HDFC':   {'preferred_bearing': 90,  'reach_factor': 1.0},  # East
    'ICICI':  {'preferred_bearing': 135, 'reach_factor': 1.1},  # Southeast
    'Axis':   {'preferred_bearing': 180, 'reach_factor': 0.9},  # South
    'PNB':    {'preferred_bearing': 225, 'reach_factor': 1.3},  # Southwest
    'Kotak':  {'preferred_bearing': 270, 'reach_factor': 0.8},  # West
    'BOB':    {'preferred_bearing': 315, 'reach_factor': 1.0},  # Northwest
    'Canara': {'preferred_bearing': 0,   'reach_factor': 1.1},  # North
}

# 4 city regions
CITY_REGIONS = [
    {'name': 'Delhi',     'district': 'Delhi',     'state': 'Delhi',        'lat_range': (28.4, 28.9), 'lon_range': (76.8, 77.4), 'weight': 0.40},
    {'name': 'Delhi NCR', 'district': 'Delhi NCR', 'state': 'Haryana',      'lat_range': (28.3, 29.0), 'lon_range': (76.5, 77.8), 'weight': 0.25},
    {'name': 'Mumbai',    'district': 'Mumbai',    'state': 'Maharashtra',  'lat_range': (18.8, 19.3), 'lon_range': (72.7, 73.1), 'weight': 0.25},
    {'name': 'Jamtara',   'district': 'Jamtara',   'state': 'Jharkhand',    'lat_range': (23.8, 24.2), 'lon_range': (86.8, 87.2), 'weight': 0.10},
]
CITY_WEIGHTS = [c['weight'] for c in CITY_REGIONS]


def pick_city():
    idx = np.random.choice(len(CITY_REGIONS), p=CITY_WEIGHTS)
    return CITY_REGIONS[idx]


def compute_alert_level(amount, hop_count):
    """Fix 2 — alert_level derived from amount + hops, not random"""
    score = 0
    if amount > 500000:   score += 2
    elif amount > 100000: score += 1
    if hop_count >= 6:    score += 2
    elif hop_count >= 4:  score += 1
    if score >= 3:   return 'HIGH'
    elif score >= 1: return 'MEDIUM'
    else:            return 'LOW'


def random_coord_near(lat, lon, hop_count, fraud_type, bank):
    """Fix 3 — displacement scales with hops + bank corridor"""
    cfg = FRAUD_TYPE_CONFIG[fraud_type]
    bank_cfg = BANK_CONFIG[bank]

    # Base displacement: 20-60km, scaled by hops and fraud type
    base_km = np.random.uniform(20, 60)
    hop_multiplier = 1 + (hop_count - 1) * 0.3  # each hop adds 30% distance
    fraud_multiplier = cfg['displacement_factor']
    reach_multiplier = bank_cfg['reach_factor']

    total_km = base_km * hop_multiplier * fraud_multiplier * reach_multiplier
    total_km = np.clip(total_km, 20, 300)

    # Direction: bank preferred bearing with noise (+/- 45 degrees)
    preferred = bank_cfg['preferred_bearing']
    bearing_deg = preferred + np.random.uniform(-45, 45)
    bearing_rad = np.radians(bearing_deg)

    displacement_deg = total_km / 111
    new_lat = lat + displacement_deg * np.cos(bearing_rad)
    new_lon = lon + displacement_deg * np.sin(bearing_rad)
    return round(new_lat, 6), round(new_lon, 6)


def generate_complaints(n=50000):
    records = []
    base_date = datetime(2024, 1, 1)

    for i in range(n):
        fraud_type = random.choice(list(FRAUD_TYPE_CONFIG.keys()))
        cfg = FRAUD_TYPE_CONFIG[fraud_type]

        amount = round(np.random.lognormal(cfg['amount_mean'], cfg['amount_std']), 2)
        amount = min(amount, 5000000)

        hop_base = np.random.randint(cfg['hop_min'], cfg['hop_max'] + 1)
        hop_extra = int(amount / 100000)
        hop_count = min(hop_base + hop_extra, 10)

        city = pick_city()
        victim_lat = round(np.random.uniform(*city['lat_range']), 6)
        victim_lon = round(np.random.uniform(*city['lon_range']), 6)

        bank = random.choice(BANKS)
        withdrawal_lat, withdrawal_lon = random_coord_near(
            victim_lat, victim_lon, hop_count, fraud_type, bank
        )

        alert_level = compute_alert_level(amount, hop_count)

        complaint_time = base_date + timedelta(
            days=np.random.randint(0, 365),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )

        records.append({
            'complaint_id':       f'CS2024{str(i+1).zfill(6)}',
            'fraud_type':         fraud_type,
            'amount_lost':        amount,
            'number_of_hops':     hop_count,
            'victim_lat':         victim_lat,
            'victim_lon':         victim_lon,
            'withdrawal_lat':     withdrawal_lat,
            'withdrawal_lon':     withdrawal_lon,
            'beneficiary_bank':   bank,
            'complaint_datetime': complaint_time,
            'victim_district':    city['district'],
            'victim_state':       city['state'],
            'status':             'closed',
            'alert_level':        alert_level,
        })

    return pd.DataFrame(records)


def verify_correlations(df):
    from scipy import stats

    corr_hops_amount, _ = stats.spearmanr(df['number_of_hops'], df['amount_lost'])
    print(f"hops vs amount: {corr_hops_amount:.3f}")

    # displacement vs hops — should be positive now
    df['displacement_km'] = np.sqrt(
        (df['withdrawal_lat'] - df['victim_lat'])**2 +
        (df['withdrawal_lon'] - df['victim_lon'])**2
    ) * 111
    corr_disp_hops, _ = stats.spearmanr(df['displacement_km'], df['number_of_hops'])
    print(f"displacement vs hops: {corr_disp_hops:.3f}  ← should be > 0.2")

    # alert_level distribution
    print("\nAlert level distribution:")
    print(df['alert_level'].value_counts())

    # alert vs amount
    print("\nMean amount by alert level:")
    print(df.groupby('alert_level')['amount_lost'].mean().sort_values(ascending=False))

    print("\nCity distribution:")
    print(df['victim_district'].value_counts())

    assert corr_hops_amount > 0.3, "FAIL: hops-amount correlation too low"
    assert corr_disp_hops > 0.2,   "FAIL: displacement not scaling with hops"
    print("\nAll checks: PASS")


def insert_into_db(df):
    inserted = 0
    for _, row in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO complaints 
                (complaint_id, fraud_type, amount_lost, number_of_hops,
                 victim_lat, victim_lon, beneficiary_bank, complaint_datetime,
                 victim_district, victim_state, status, alert_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (complaint_id) DO NOTHING
            """, (
                row['complaint_id'], row['fraud_type'], row['amount_lost'],
                row['number_of_hops'], row['victim_lat'], row['victim_lon'],
                row['beneficiary_bank'], row['complaint_datetime'],
                row['victim_district'], row['victim_state'],
                row['status'], row['alert_level']
            ))
            conn.commit()
            inserted += 1
        except Exception as e:
            conn.rollback()
            print(f"Row error: {e}")
            break
    print(f"Inserted {inserted} complaints into database")


if __name__ == "__main__":
    print("Generating synthetic data...")
    df = generate_complaints(50000)
    df.to_csv('synthetic_complaints.csv', index=False)
    print("CSV saved")
    verify_correlations(df)
    insert_into_db(df)
    cur.close()
    conn.close()