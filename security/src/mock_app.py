from fastapi import FastAPI, Request, Depends
from rate_limiter import check_rate_limit
from rbac import create_token, require_role
from audit_log import log_event
from pii_masking import mask_phone, mask_email

app = FastAPI()

FAKE_USERS = {
    "investigator1": {"password": "pass123", "role": "investigator"},
    "bankofficer1": {"password": "pass123", "role": "bank_officer"},
    "admin1": {"password": "pass123", "role": "admin"},
}


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


@app.get("/investigator-only")
def investigator_route(user=Depends(require_role("investigator"))):
    return {"message": f"Welcome investigator {user['sub']}"}


@app.get("/admin-only")
def admin_route(user=Depends(require_role("admin"))):
    return {"message": f"Welcome admin {user['sub']}"}


@app.get("/sample-masked-data")
def sample_masked_data():
    return {
        "phone": mask_phone("9876543210"),
        "email": mask_email("victim@example.com"),
    }