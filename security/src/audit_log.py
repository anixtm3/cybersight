import json
import time

LOG_FILE = "audit_log.jsonl"


def log_event(event_type: str, actor: str, status: str, detail: str = ""):
    entry = {
        "event_type": event_type,
        "actor": actor,
        "status": status,
        "detail": detail,
        "timestamp": time.time(),
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")