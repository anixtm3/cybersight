from fastapi import FastAPI, Request, Depends
from rate_limiter import check_rate_limit
from rbac import create_token, require_role
from audit_log import log_event
from pii_masking import mask_phone, mask_email
from alert_dispatch import dispatch_alert

app = FastAPI()

FAKE_USERS = {
    "officer1": {"password": "pass123", "role": "cyber_cell_officer"},
    "bankofficer1": {"password": "pass123", "role": "bank_nodal_officer"},
    "admin1": {"password": "pass123", "role": "admin"},
}

EVIDENCE_LOG = []


@app.post("/login")
def login(request: Request, username: str, password: str):
    check_rate_limit(request)
    user = FAKE_USERS.get(username)
    if not user or user["password"] != password:
        log_event("AUTH_LOGIN", username, "FAILED")
        return {"error": "Invalid credentials"}
    token = create_token(username, user["role"])
    log_event("AUTH_LOGIN", username, "SUCCESS")
    return {"access_token": token, "role": user["role"]}


@app.get("/cyber-cell-only")
def cyber_cell_route(user=Depends(require_role("cyber_cell_officer"))):
    return {"message": f"Welcome cyber cell officer {user['sub']}"}


@app.get("/admin-only")
def admin_route(user=Depends(require_role("admin"))):
    return {"message": f"Welcome admin {user['sub']}"}


@app.get("/sample-masked-data")
def sample_masked_data():
    return {
        "phone": mask_phone("9876543210"),
        "email": mask_email("victim@example.com"),
    }


@app.post("/evidence-log")
def add_evidence_entry(
    case_id: str,
    action_type: str,
    notes: str,
    user=Depends(require_role("cyber_cell_officer")),
):
    entry = {
        "case_id": case_id,
        "investigator": user["sub"],
        "action_type": action_type,
        "notes": notes,
    }
    EVIDENCE_LOG.append(entry)
    log_event(
        "EVIDENCE_ACCESS", user["sub"], "SUCCESS",
        detail=f"{action_type} on case {case_id}",
    )
    return {"status": "logged", "entry": entry}


@app.get("/evidence-log/{case_id}")
def get_evidence_log(case_id: str, user=Depends(require_role("cyber_cell_officer"))):
    matching = [e for e in EVIDENCE_LOG if e["case_id"] == case_id]
    return {"case_id": case_id, "entries": matching}


@app.post("/trigger-alert")
def trigger_alert(zone: str, risk_level: str, user=Depends(require_role("admin"))):
    recipients = {"phone": "9876543210", "email": "leo@example.com"}
    results = dispatch_alert(zone, risk_level, recipients)
    return {"dispatched": results}