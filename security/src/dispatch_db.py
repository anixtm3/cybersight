import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = "dispatch_log_test.db"


def init_dispatch_log_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dispatch_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id VARCHAR(50),
            channel VARCHAR(20) NOT NULL,
            recipient TEXT NOT NULL,
            dispatched_at TEXT,
            delivery_status VARCHAR(20),
            raw_response TEXT
        )
    """)
    conn.commit()
    conn.close()


def write_dispatch_log(complaint_id, channel, recipient, delivery_status, raw_response=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO dispatch_log
        (complaint_id, channel, recipient, dispatched_at, delivery_status, raw_response)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            complaint_id,
            channel,
            recipient,
            datetime.now(timezone.utc).isoformat(),
            delivery_status,
            json.dumps(raw_response) if raw_response else None,
        ),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_dispatch_logs(complaint_id=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if complaint_id:
        cur.execute("SELECT * FROM dispatch_log WHERE complaint_id = ?", (complaint_id,))
    else:
        cur.execute("SELECT * FROM dispatch_log")
    rows = cur.fetchall()
    conn.close()
    return rows