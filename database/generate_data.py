import os
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname="cybersight",
    user="postgres",
    password=os.environ.get("DB_PASSWORD", ""),
    host="localhost",
    port="5433"
)
cur = conn.cursor()
conn.autocommit = True

FRAUD_TYPE_CONFIG = {
    'UPI Fraud':          {'hop_min': 2, 'hop_max': 4,  'amount_mean': 8,  'amount_std': 1.2, 'displacement_factor': 1.0, 'account_age_mean': 180, 'account_age_std': 60},
    'OLX Scam':           {'hop_min': 1, 'hop_max': 3,  'amount_mean': 9,  'amount_std': 1.0, 'displacement_factor': 0.8, 'account_age_mean': 90,  'account_age_std': 30},
    'Investment Scam':    {'hop_min': 4, 'hop_max': 7,  'amount_mean': 11, 'amount_std': 1.5, 'displacement_factor': 2.0, 'account_age_mean': 365, 'account_age_std': 90},
    'Romance Scam':       {'hop_min': 3, 'hop_max': 6,  'amount_mean': 10, 'amount_std': 1.3, 'displacement_factor': 1.8, 'account_age_mean': 300, 'account_age_std': 80},
    'KYC Fraud':          {'hop_min': 2, 'hop_max': 4,  'amount_mean': 7,  'amount_std': 1.0, 'displacement_factor': 1.0, 'account_age_mean': 120, 'account_age_std': 45},
    'Job Fraud':          {'hop_min': 1, 'hop_max': 3,  'amount_mean': 7,  'amount_std': 0.9, 'displacement_factor': 0.7, 'account_age_mean': 60,  'account_age_std': 20},
    'Lottery Fraud':      {'hop_min': 2, 'hop_max': 5,  'amount_mean': 9,  'amount_std': 1.1, 'displacement_factor': 1.2, 'account_age_mean': 200, 'account_age_std': 70},
    'Tech Support Fraud': {'hop_min': 1, 'hop_max': 3,  'amount_mean': 8,  'amount_std': 1.0, 'displacement_factor': 0.6, 'account_age_mean': 150, 'account_age_std': 50},
}

BANKS = ['SBI', 'HDFC', 'ICICI', 'Axis', 'PNB', 'Kotak', 'BOB', 'Canara']

BANK_CONFIG = {
    'SBI':    {'reach_factor': 1.2},
    'HDFC':   {'reach_factor': 1.0},
    'ICICI':  {'reach_factor': 1.1},
    'Axis':   {'reach_factor': 0.9},
    'PNB':    {'reach_factor': 1.3},
    'Kotak':  {'reach_factor': 0.8},
    'BOB':    {'reach_factor': 1.0},
    'Canara': {'reach_factor': 1.1},
}

CITY_REGIONS = [
    {'name': 'Delhi',     'district': 'Delhi',     'state': 'Delhi',         'lat_range': (28.4, 28.9), 'lon_range': (76.8, 77.4), 'weight': 0.20},
    {'name': 'Delhi NCR', 'district': 'Delhi NCR', 'state': 'Haryana',       'lat_range': (28.3, 29.0), 'lon_range': (76.5, 77.8), 'weight': 0.15},
    {'name': 'Mumbai',    'district': 'Mumbai',    'state': 'Maharashtra',   'lat_range': (18.8, 19.3), 'lon_range': (72.7, 73.1), 'weight': 0.15},
    {'name': 'Jamtara',   'district': 'Jamtara',   'state': 'Jharkhand',     'lat_range': (23.8, 24.2), 'lon_range': (86.8, 87.2), 'weight': 0.10},
    {'name': 'Bengaluru', 'district': 'Bengaluru', 'state': 'Karnataka',     'lat_range': (12.8, 13.1), 'lon_range': (77.4, 77.8), 'weight': 0.10},
    {'name': 'Hyderabad', 'district': 'Hyderabad', 'state': 'Telangana',     'lat_range': (17.2, 17.6), 'lon_range': (78.3, 78.6), 'weight': 0.08},
    {'name': 'Agra',      'district': 'Agra',      'state': 'Uttar Pradesh', 'lat_range': (26.9, 27.3), 'lon_range': (77.9, 78.2), 'weight': 0.08},
    {'name': 'Patna',     'district': 'Patna',     'state': 'Bihar',         'lat_range': (25.5, 25.8), 'lon_range': (85.0, 85.3), 'weight': 0.07},
    {'name': 'Pune',      'district': 'Pune',      'state': 'Maharashtra',   'lat_range': (18.4, 18.7), 'lon_range': (73.7, 74.0), 'weight': 0.04},
    {'name': 'Lucknow',   'district': 'Lucknow',   'state': 'Uttar Pradesh', 'lat_range': (26.7, 27.0), 'lon_range': (80.8, 81.1), 'weight': 0.03},
]
CITY_WEIGHTS = [c['weight'] for c in CITY_REGIONS]

FESTIVAL_DATES = set()
for month, day in [
    (1,14),(1,15),(1,22),(3,25),(4,11),(4,14),(4,17),
    (6,17),(8,15),(8,19),(8,26),(10,2),(10,12),(10,13),
    (10,24),(11,1),(11,2),(11,3),(11,15),(12,25)
]:
    FESTIVAL_DATES.add((2024, month, day))


def pick_city():
    idx = np.random.choice(len(CITY_REGIONS), p=CITY_WEIGHTS)
    return CITY_REGIONS[idx]


def compute_alert_level(amount, hop_count):
    score = 0
    if amount > 500000:   score += 2
    elif amount > 100000: score += 1
    if hop_count >= 6:    score += 2
    elif hop_count >= 4:  score += 1
    if score >= 3:   return 'HIGH'
    elif score >= 1: return 'MEDIUM'
    else:            return 'LOW'


def random_coord_near(lat, lon, hop_count, fraud_type, bank, is_insider=False):
    if is_insider:
        displacement_km = np.random.uniform(2, 5)
        angle = np.random.uniform(0, 2 * np.pi)
        displacement_deg = displacement_km / 111
        return round(lat + displacement_deg * np.cos(angle), 6), \
               round(lon + displacement_deg * np.sin(angle), 6)

    cfg = FRAUD_TYPE_CONFIG[fraud_type]
    bank_cfg = BANK_CONFIG[bank]
    base_km = np.random.uniform(20, 60)
    hop_multiplier = 1 + (hop_count - 1) * 0.3
    total_km = base_km * hop_multiplier * cfg['displacement_factor'] * bank_cfg['reach_factor']
    total_km = np.clip(total_km, 20, 300)
    bearing_rad = np.random.uniform(0, 2 * np.pi)
    displacement_deg = total_km / 111
    return round(lat + displacement_deg * np.cos(bearing_rad), 6), \
           round(lon + displacement_deg * np.sin(bearing_rad), 6)


def fetch_nearest_atm(withdrawal_lat, withdrawal_lon):
    try:
        lon = float(withdrawal_lon)
        lat = float(withdrawal_lat)
        cur.execute("""
            SELECT atm_id,
                ST_Distance(
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    location::geography
                ) / 1000 as distance_km
            FROM atm_locations
            ORDER BY location <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            LIMIT 1
        """, (lon, lat, lon, lat))
        row = cur.fetchone()
        return (row[0], round(row[1], 2)) if row else (None, None)
    except Exception as e:
        print(f"ATM fetch error: {e}")
        return None, None


def fetch_atm_density(withdrawal_lat, withdrawal_lon, radius_km=5):
    try:
        lon = float(withdrawal_lon)
        lat = float(withdrawal_lat)
        cur.execute("""
            SELECT COUNT(*) FROM atm_locations
            WHERE ST_DWithin(
                location::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
        """, (lon, lat, radius_km * 1000))
        row = cur.fetchone()
        return int(row[0]) if row else 0
    except Exception as e:
        print(f"ATM density error: {e}")
        return 0


def generate_complaints(n=400001, start_index=100000):
    records = []
    base_date = datetime(2024, 1, 1)
    print(f"Generating {n} complaints from index {start_index}...")

    for i in range(n):
        if i % 5000 == 0:
            print(f"  {start_index + i}/{start_index + n}...")

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
        is_insider = np.random.random() < 0.05

        withdrawal_lat, withdrawal_lon = random_coord_near(
            victim_lat, victim_lon, hop_count, fraud_type, bank, is_insider
        )

        target_atm_id, atm_distance_km = fetch_nearest_atm(withdrawal_lat, withdrawal_lon)
        atm_density = fetch_atm_density(withdrawal_lat, withdrawal_lon)
        alert_level = compute_alert_level(amount, hop_count)

        complaint_time = base_date + timedelta(
            days=np.random.randint(0, 365),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )

        hour = complaint_time.hour
        hour_sin = round(np.sin(2 * np.pi * hour / 24), 6)
        hour_cos = round(np.cos(2 * np.pi * hour / 24), 6)
        day_of_week = complaint_time.weekday()
        is_weekend = day_of_week >= 5
        is_festival = (complaint_time.year, complaint_time.month, complaint_time.day) in FESTIVAL_DATES

        account_age_days = max(1, int(np.random.normal(
            cfg['account_age_mean'], cfg['account_age_std']
        )))

        mule_prob = 0.05 + (hop_count / 10) * 0.25
        mule_network_flag = np.random.random() < mule_prob

        displacement_km = round(np.sqrt(
            (withdrawal_lat - victim_lat) ** 2 +
            (withdrawal_lon - victim_lon) ** 2
        ) * 111, 2)

        records.append({
            'complaint_id':                     f'CS2024{str(start_index + i + 1).zfill(6)}',
            'fraud_type':                       fraud_type,
            'amount_lost':                      amount,
            'number_of_hops':                   hop_count,
            'victim_lat':                       victim_lat,
            'victim_lon':                       victim_lon,
            'withdrawal_lat':                   withdrawal_lat,
            'withdrawal_lon':                   withdrawal_lon,
            'target_atm_id':                    target_atm_id,
            'beneficiary_bank':                 bank,
            'complaint_datetime':               complaint_time,
            'victim_district':                  city['district'],
            'victim_state':                     city['state'],
            'status':                           'closed',
            'alert_level':                      alert_level,
            'is_insider_case':                  is_insider,
            'account_age_days':                 account_age_days,
            'mule_network_flag':                mule_network_flag,
            'is_festival_period':               is_festival,
            'hour_of_day_sin':                  hour_sin,
            'hour_of_day_cos':                  hour_cos,
            'day_of_week':                      day_of_week,
            'is_weekend':                       is_weekend,
            'victim_to_withdrawal_distance_km': displacement_km,
            'atm_density':                      atm_density,
        })

    df = pd.DataFrame(records)

    print("Computing rolling features...")
    df['complaint_datetime'] = pd.to_datetime(df['complaint_datetime'])
    df = df.sort_values('complaint_datetime').reset_index(drop=True)

    rolling_result = np.zeros(len(df), dtype=int)
    for district in df['victim_district'].unique():
        mask = df['victim_district'] == district
        idx = np.where(mask)[0]
        times = df.loc[mask, 'complaint_datetime'].values.astype(np.int64)
        window_ns = 6 * 3600 * 1_000_000_000
        for j in range(len(times)):
            rolling_result[idx[j]] = int(np.sum(
                (times[:j] >= times[j] - window_ns) & (times[:j] < times[j])
            ))
    df['rolling_6h_complaint_count'] = rolling_result

    df['time_since_last_complaint_same_bank'] = -1.0
    for bank in df['beneficiary_bank'].unique():
        mask = df['beneficiary_bank'] == bank
        bank_df = df[mask].sort_values('complaint_datetime')
        shifted = bank_df['complaint_datetime'].shift(1)
        diff_hours = (bank_df['complaint_datetime'] - shifted).dt.total_seconds() / 3600
        df.loc[bank_df.index, 'time_since_last_complaint_same_bank'] = diff_hours.values

    district_counts = df['victim_district'].value_counts()
    max_count = district_counts.max()
    df['district_risk_score'] = df['victim_district'].map(
        lambda d: round(district_counts.get(d, 0) / max_count, 4)
    )

    return df


def verify_correlations(df):
    from scipy import stats
    print("\n── Verification ──")
    corr, _ = stats.spearmanr(df['number_of_hops'], df['amount_lost'])
    print(f"hops vs amount:       {corr:.3f}  (should be > 0.3)")
    corr2, _ = stats.spearmanr(df['victim_to_withdrawal_distance_km'], df['number_of_hops'])
    print(f"displacement vs hops: {corr2:.3f}  (should be > 0.2)")
    print(f"insider cases:        {df['is_insider_case'].sum()} ({df['is_insider_case'].mean()*100:.1f}%)")
    print(f"festival rows:        {df['is_festival_period'].sum()}")
    print(f"mule flag TRUE:       {df['mule_network_flag'].sum()} ({df['mule_network_flag'].mean()*100:.1f}%)")
    print(f"target_atm nulls:     {df['target_atm_id'].isna().sum()}")
    print(f"\nDistrict distribution:\n{df['victim_district'].value_counts()}")
    assert corr > 0.3,  "FAIL: hops-amount correlation too low"
    assert corr2 > 0.2, "FAIL: displacement not scaling with hops"
    print("\nAll checks: PASS")


def insert_into_db(df):
    print("\nInserting into DB...")
    inserted = 0
    for _, row in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO complaints
                (complaint_id, fraud_type, amount_lost, number_of_hops,
                 victim_lat, victim_lon, withdrawal_lat, withdrawal_lon,
                 target_atm_id, beneficiary_bank, complaint_datetime,
                 victim_district, victim_state, status, alert_level,
                 is_insider_case, account_age_days, mule_network_flag,
                 is_festival_period, hour_of_day_sin, hour_of_day_cos,
                 victim_to_withdrawal_distance_km, atm_density,
                 rolling_6h_complaint_count, time_since_last_complaint_same_bank,
                 district_risk_score)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (complaint_id) DO NOTHING
            """, (
                row['complaint_id'], row['fraud_type'], row['amount_lost'],
                row['number_of_hops'], row['victim_lat'], row['victim_lon'],
                row['withdrawal_lat'], row['withdrawal_lon'], row['target_atm_id'],
                row['beneficiary_bank'], row['complaint_datetime'],
                row['victim_district'], row['victim_state'], row['status'],
                row['alert_level'], bool(row['is_insider_case']),
                int(row['account_age_days']), bool(row['mule_network_flag']),
                bool(row['is_festival_period']),
                float(row['hour_of_day_sin']), float(row['hour_of_day_cos']),
                float(row['victim_to_withdrawal_distance_km']),
                int(row['atm_density']),
                int(row['rolling_6h_complaint_count']),
                float(row['time_since_last_complaint_same_bank']),
                float(row['district_risk_score'])
            ))
            inserted += 1
            if inserted % 10000 == 0:
                print(f"  Inserted {inserted}...")
        except Exception as e:
            print(f"Row error at {row['complaint_id']}: {e}")
            break
    print(f"Inserted {inserted} complaints")


if __name__ == "__main__":
    df = generate_complaints(n=400001, start_index=100000)
    df.to_csv('synthetic_complaints_remaining.csv', index=False)
    size_mb = os.path.getsize('synthetic_complaints_remaining.csv') / 1024 / 1024
    print(f"\nCSV saved — size: {size_mb:.1f} MB")
    verify_correlations(df)
    insert_into_db(df)
    cur.close()
    conn.close()