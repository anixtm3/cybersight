import os
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import random

# Database connection
conn = psycopg2.connect(
    dbname="cybersight",
    user="postgres",
    password=os.environ.get("DB_PASSWORD", "33aA2#bB"),
    host="localhost",
    port="5433"
)
cur = conn.cursor()

# Causal rules
FRAUD_TYPE_CONFIG = {
    'UPI Fraud':         {'hop_min': 2, 'hop_max': 4, 'amount_mean': 8,  'amount_std': 1.2},
    'OLX Scam':          {'hop_min': 1, 'hop_max': 3, 'amount_mean': 9,  'amount_std': 1.0},
    'Investment Scam':   {'hop_min': 4, 'hop_max': 7, 'amount_mean': 11, 'amount_std': 1.5},
    'Romance Scam':      {'hop_min': 3, 'hop_max': 6, 'amount_mean': 10, 'amount_std': 1.3},
    'KYC Fraud':         {'hop_min': 2, 'hop_max': 4, 'amount_mean': 7,  'amount_std': 1.0},
    'Job Fraud':         {'hop_min': 1, 'hop_max': 3, 'amount_mean': 7,  'amount_std': 0.9},
    'Lottery Fraud':     {'hop_min': 2, 'hop_max': 5, 'amount_mean': 9,  'amount_std': 1.1},
    'Tech Support Fraud':{'hop_min': 1, 'hop_max': 3, 'amount_mean': 8,  'amount_std': 1.0},
}

BANKS = ['SBI', 'HDFC', 'ICICI', 'Axis', 'PNB', 'Kotak', 'BOB', 'Canara']

# 4 city regions with weights and metadata
CITY_REGIONS = [
    {
        'name': 'Delhi',
        'district': 'Delhi',
        'state': 'Delhi',
        'lat_range': (28.4, 28.9),
        'lon_range': (76.8, 77.4),
        'weight': 0.40
    },
    {
        'name': 'Delhi NCR',
        'district': 'Delhi NCR',
        'state': 'Haryana',
        'lat_range': (28.3, 29.0),
        'lon_range': (76.5, 77.8),
        'weight': 0.25
    },
    {
        'name': 'Mumbai',
        'district': 'Mumbai',
        'state': 'Maharashtra',
        'lat_range': (18.8, 19.3),
        'lon_range': (72.7, 73.1),
        'weight': 0.25
    },
    {
        'name': 'Jamtara',
        'district': 'Jamtara',
        'state': 'Jharkhand',
        'lat_range': (23.8, 24.2),
        'lon_range': (86.8, 87.2),
        'weight': 0.10
    },
]

CITY_WEIGHTS = [c['weight'] for c in CITY_REGIONS]


def pick_city():
    """Weighted random city selection"""
    idx = np.random.choice(len(CITY_REGIONS), p=CITY_WEIGHTS)
    return CITY_REGIONS[idx]


def random_coord_near(lat, lon, min_km=20, max_km=120):
    """Withdrawal displaced 20-120km from victim"""
    displacement_deg = np.random.uniform(min_km, max_km) / 111
    angle = np.random.uniform(0, 2 * np.pi)
    new_lat = lat + displacement_deg * np.cos(angle)
    new_lon = lon + displacement_deg * np.sin(angle)
    return round(new_lat, 6), round(new_lon, 6)


def generate_complaints(n=50000):
    records = []
    base_date = datetime(2024, 1, 1)

    for i in range(n):
        fraud_type = random.choice(list(FRAUD_TYPE_CONFIG.keys()))
        cfg = FRAUD_TYPE_CONFIG[fraud_type]

        amount = round(np.random.lognormal(cfg['amount_mean'], cfg['amount_std']), 2)
        amount = min(amount, 5000000)  # cap at 50 lakh

        # hop count correlates with amount
        hop_base = np.random.randint(cfg['hop_min'], cfg['hop_max'] + 1)
        hop_extra = int(amount / 100000)
        hop_count = min(hop_base + hop_extra, 10)

        # pick city
        city = pick_city()
        victim_lat = round(np.random.uniform(*city['lat_range']), 6)
        victim_lon = round(np.random.uniform(*city['lon_range']), 6)

        # withdrawal displaced from victim
        withdrawal_lat, withdrawal_lon = random_coord_near(victim_lat, victim_lon)

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
            'beneficiary_bank':   random.choice(BANKS),
            'complaint_datetime': complaint_time,
            'victim_district':    city['district'],
            'victim_state':       city['state'],
            'status':             'closed',
            'alert_level':        random.choice(['LOW', 'MEDIUM', 'HIGH'])
        })

    return pd.DataFrame(records)


def verify_correlations(df):
    from scipy import stats
    corr, pval = stats.spearmanr(df['number_of_hops'], df['amount_lost'])
    print(f"hop_count vs amount correlation: {corr:.3f} (p={pval:.4f})")

    same_area = (df['victim_lat'].round(1) == df['withdrawal_lat'].round(1)).mean()
    print(f"Same-area rate: {same_area:.2%}")

    # City distribution check
    print("\nCity distribution:")
    print(df['victim_district'].value_counts())

    assert corr > 0.3, "FAIL: correlation too low"
    assert same_area < 0.1, "FAIL: withdrawal too close to victim"
    print("\nCorrelation check: PASS")


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