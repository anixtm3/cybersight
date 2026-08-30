import json, psycopg2, os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(dbname="cybersight", user="postgres",
    password=os.environ.get("DB_PASSWORD", ""), host="localhost", port="5433")
cur = conn.cursor()

with open(r'C:\Users\SAINA20\Downloads\lucknow_atms.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

inserted = 0
for i, feature in enumerate(data['features']):
    geom = feature.get('geometry', {})
    if geom.get('type') != 'Point':
        continue
    lon, lat = geom['coordinates']
    props = feature.get('properties', {})
    bank_name = props.get('operator') or props.get('name') or props.get('brand') or 'Unknown Bank'
    atm_id = f"LKO{str(i+1).zfill(5)}"
    try:
        cur.execute("""
            INSERT INTO atm_locations (atm_id, bank_name, address, district, state, location)
            VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ON CONFLICT (atm_id) DO NOTHING
        """, (atm_id, bank_name, props.get('addr:full', ''), 'Lucknow', 'Uttar Pradesh', lon, lat))
        conn.commit()
        inserted += 1
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

print(f"Inserted: {inserted} Lucknow ATMs")
cur.close()
conn.close()