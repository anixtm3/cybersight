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


### Test 4 - Automated Test Suite (pytest)

Twelve automated tests covering PII masking (phone, email, account,
Aadhaar, PAN, address), password hashing/verification, JWT token
creation, and multi-channel alert dispatch (SMS, email, webhook).

Run with: `pytest test_security.py -v` (from `security/src`)

Result: 12 passed, 1 warning (JWT key length recommendation, non-blocking)

All independently verifiable, repeatable via a single command.


### Test 5 - Evidence Documentation and Alert Trigger Endpoints

Three additional endpoint tests added to the automated suite:

- Evidence log entry created and retrieved successfully by an
  investigator role
- Evidence log write correctly denied (403) for a non-investigator
  role (admin)
- Alert trigger endpoint correctly denied (403) for a non-admin role
  (investigator), and correctly succeeds (200) for admin, dispatching
  to 2 channels

Total automated test count: 15 (all passing).


### Test 6 - Role Sync with Confirmed Backend Contract

Roles updated to match confirmed backend contract from Kartike:
admin, cyber_cell_officer, bank_nodal_officer (previously used
placeholder names: investigator, bank_officer, admin).

### Test 7 - Jurisdiction-Scoped Authorization

Added `require_jurisdiction()` dependency in rbac.py, ready for the
`jurisdiction` JWT claim once added by the backend team. Three
scenarios tested:

- Same-district access: user jurisdiction matches resource
  jurisdiction -> 200 OK
- Cross-district access: user jurisdiction does not match resource
  jurisdiction -> 403 Forbidden
- Admin bypass: admin role skips jurisdiction check entirely -> 200 OK

Total automated test count: 19 (all passing).


### Test 8 - Dispatch Log Database Integration

Wired alert_dispatch.py to a database (SQLite for local testing,
schema matching Kartike's confirmed dispatch_log table exactly:
id, complaint_id, channel, recipient, dispatched_at, delivery_status,
raw_response).

Verified: every dispatch (SMS, email, webhook) writes a row with
correct column values matching the schema. Sample verified rows:

- SMS: channel=sms, recipient=phone number, delivery_status=SENT
- Email: channel=email, recipient=email address, delivery_status=SENT
- Webhook: channel=webhook, recipient=URL, delivery_status=SENT

Migration to production (Postgres) requires only a connection-string
change; the write logic and schema already match Kartike's model.

Total automated test count: 19 (all still passing after DB wiring).


### Test 9 - Real Backend Integration (Live Test)

Tested against Kartike's live backend via public tunnel
(https://solid-peas-eat.loca.lt), not the mock environment.

**Health check:**
GET /health -> 200 OK, {"status":"ok"}

**Real login:**
POST /api/auth/login
Body: {"username": "officer_delhi", "password": "Test@123"}
Result: 200 OK, real access_token returned

**JWT decode (real token, not self-issued):**
{
  "sub": "officer_delhi",
  "role": "cyber_cell_officer",
  "jurisdiction": "New Delhi",
  "bank_name": null,
  "exp": 1788026580
}

**Jurisdiction enforcement verified against real token:**
require_jurisdiction() logic checked manually against the decoded
real payload for a "New Delhi" resource - correctly grants access
on jurisdiction match. No backend changes were required; the
existing require_jurisdiction() implementation in rbac.py works
as-is with Kartike's real JWT structure.

This confirms the security module's RBAC and jurisdiction logic is
compatible with the actual backend contract, not just the mock
environment used for earlier tests.


### Test 10 - WebSocket Authentication (/ws/alerts)

Implemented per Kartike's confirmed contract: JWT-gated (not public),
token sent in the first message after connect (not query param, to
avoid token leaking into server/tunnel logs), invalid/expired/missing
token results in socket close with code 4001 and a reason string.

Three scenarios tested:

- Valid token: connection succeeds, authenticated user data returned
- Missing token in first message: connection closed with code 4001
- Invalid/malformed token: connection closed with code 4001

Total automated test count: 22 (all passing).
Code: security/src/ws_auth.py (authenticate_websocket function),
using rbac.get_current_user_from_token() for token validation
outside the HTTP Header dependency context.


### Test 11 - All 10 Real Districts Verified

Saina confirmed final DB schema and the 10 real district names used
in production: Delhi, Delhi NCR, Mumbai, Jamtara, Bengaluru,
Hyderabad, Agra, Patna, Pune, Lucknow.

require_jurisdiction() tested against all 10 districts individually
(same-district access) plus 5 cross-district pairs (access denial):

- All 10 same-district cases: 200 OK, access granted
- All 5 cross-district cases: 403 Forbidden, access denied

Total automated test count: 37 (34 passing, 3 skipped pending
merge into Kartike's backend for ws_auth.py-dependent tests).

Field mapping confirmed: DB column jurisdiction_district maps to
JWT claim jurisdiction (intentional naming difference per Kartike's
auth_core.py design) - no code change required in require_jurisdiction().