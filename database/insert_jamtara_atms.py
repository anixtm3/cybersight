import psycopg2
import os
import numpy as np
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

BANKS = ['SBI', 'PNB', 'Bank of India', 'Canara Bank', 'UCO Bank', 'BOB']

np.random.seed(42)
inserted = 0

for i in range(300):
    lat = round(np.random.uniform(23.8, 24.2), 6)
    lon = round(np.random.uniform(86.8, 87.2), 6)
    bank = np.random.choice(BANKS)
    atm_id = f"JAM{str(i+1).zfill(5)}"

    try:
        cur.execute("""
            INSERT INTO atm_locations (atm_id, bank_name, district, state, location)
            VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ON CONFLICT (atm_id) DO NOTHING
        """, (atm_id, bank, 'Jamtara', 'Jharkhand', lon, lat))
        conn.commit()
        inserted += 1
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

print(f"Inserted: {inserted} Jamtara ATMs")
cur.close()
conn.close()