## 11. Testing Evidence - Independent Verification

### Objective

Working test evidence for security components that could be
verified independently of the confirmed backend contract, using a
standalone mock FastAPI application (security/src/mock_app.py).

Backend-integrated testing (real user model, real database) remains
pending confirmation of the auth contract from the backend team.

### Test Environment

- Mock app: security/src/mock_app.py
- Modules under test: pii_masking.py, rate_limiter.py, rbac.py, audit_log.py
- Run with: uvicorn mock_app:app --port 8001 (from security/src)
- Three fake users seeded: investigator1, bankofficer1, admin1

### Test 1 - PII Masking

Request: GET /sample-masked-data

Result: 200 OK

{"phone":"XXXXXX3210","email":"v****m@example.com"}

Phone number masked to last 4 digits. Email masked except first and
last character of local part. PASS.

### Test 2 - RBAC (Role-Based Access Control)

Three users logged in successfully with distinct roles:

- investigator1 -> role: investigator
- bankofficer1 -> role: bank_officer
- admin1 -> role: admin

Access control verified on role-restricted route /investigator-only:

- Admin token on /investigator-only -> 403 Forbidden
  {"detail":"Access denied. Requires role: investigator"}
- Investigator token on /investigator-only -> 200 OK
  {"message":"Welcome investigator investigator1"}

Role mismatch correctly denied, matching role correctly allowed. PASS.

### Test 3 - Rate Limiting

Six rapid login requests sent to POST /login for the same user
within the rate-limit window (5 attempts / 60 seconds).

- Attempts 1 to 5: 200 OK, access token returned each time
- Attempt 6: 429 Too Many Requests
  {"detail":"Too many login attempts. Try again in 60 seconds."}

Rate limit correctly enforced after 5 attempts. PASS.

### Summary

| Test | Result |
|---|---|
| PII Masking | PASS |
| RBAC | PASS |
| Rate Limiting | PASS |

### Current Status

All three items independently verified using a standalone mock
environment, without requiring the confirmed backend contract.
Integration testing against the real backend (Saina/Kartike) will
follow once the auth contract is finalized.
