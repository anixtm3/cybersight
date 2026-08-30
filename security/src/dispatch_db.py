import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone

DB_HOST = os.environ.get("CYBERSIGHT_DB_HOST", "localhost")
DB_PORT = os.environ.get("CYBERSIGHT_DB_PORT", "5433")
DB_NAME = os.environ.get("CYBERSIGHT_DB_NAME", "cybersight")
DB_USER = os.environ.get("CYBERSIGHT_DB_USER", "postgres")
DB_PASSWORD = os.environ.get("CYBERSIGHT_DB_PASSWORD", "")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_dispatch_log_table():
    try:
        conn = get_connection()
    except Exception as e:
        print(f"[dispatch_db] Could not connect to Postgres, skipping table init: {e}")
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dispatch_log (
            id SERIAL PRIMARY KEY,
            complaint_id VARCHAR(50),
            channel VARCHAR(20) NOT NULL,
            recipient TEXT NOT NULL,
            dispatched_at TIMESTAMPTZ DEFAULT now(),
            delivery_status VARCHAR(20),
            raw_response TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def write_dispatch_log(complaint_id, channel, recipient, delivery_status, raw_response=None):
    try:
        conn = get_connection()
    except Exception as e:
        print(f"[dispatch_db] Could not connect to Postgres, skipping DB write: {e}")
        return None

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO dispatch_log
        (complaint_id, channel, recipient, dispatched_at, delivery_status, raw_response)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            complaint_id,
            channel,
            recipient,
            datetime.now(timezone.utc),
            delivery_status,
            json.dumps(raw_response) if raw_response else None,
        ),
    )
    row_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return row_id


def get_dispatch_logs(complaint_id=None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if complaint_id:
        cur.execute("SELECT * FROM dispatch_log WHERE complaint_id = %s", (complaint_id,))
    else:
        cur.execute("SELECT * FROM dispatch_log")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows