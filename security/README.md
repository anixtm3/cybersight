# Security Module - CyberSight

**Developer:** Kanav Agarwal
**Role:** Security Engineer
**Branch:** kanav

This folder documents the security design for CyberSight - covering
authentication, authorization, rate limiting, PII protection, and
audit logging.

## Status

Day 1-2 - Security foundation, design, and core logic implemented
and tested. Roles synced with confirmed backend contract
(admin, cyber_cell_officer, bank_nodal_officer). Jurisdiction-scoped
authorization implemented and tested using the confirmed JWT
claim. Alert dispatcher wired to a database matching Kartike's
dispatch_log schema exactly (SQLite locally, drop-in replacement
for Postgres in production). Full backend integration (real login
endpoint) is in progress pending backend URL/access from Kartike.

## Files

| File | Covers |
|---|---|
| 00-overview.md | Security engineering overview |
| 01-security-objective.md | Overall security goals |
| 02-day-1-scope.md | Day 1 scope and boundaries |
| 03-security-principles.md | Core security principles followed |
| 04-current-integration-decisions.md | Integration decisions made so far |
| 05-day-1-status.md | Current status of Day 1 work |
| 06-jwt-authentication-token-security.md | JWT auth, access/refresh tokens, revocation |
| 07-rbac-jurisdiction-scoped-authorization.md | Role-based access control, jurisdiction scoping |
| 08-rate-limiting-api-abuse-protection.md | Rate limiting and API abuse protection |
| 09-pii-protection-data-privacy.md | PII masking and data minimization |
| 10-audit-logging-security-events.md | Audit logging and security event tracking |
| 11-testing-evidence.md | Independent testing evidence (all modules, 19 pytest tests) |

## Code

| File | Covers |
|---|---|
| src/pii_masking.py | Phone, email, account, Aadhaar, PAN, address masking functions |
| src/rate_limiter.py | In-memory rate limiter (5 attempts / 60 seconds) |
| src/rbac.py | JWT token creation, decoding, role-based and jurisdiction-based access dependencies |
| src/audit_log.py | JSON-lines audit event logger |
| src/password_security.py | Password hashing and verification using bcrypt |
| src/alert_dispatch.py | Multi-channel alert dispatch (SMS, email, webhook), wired to dispatch_log DB |
| src/dispatch_db.py | Database layer matching Kartike's confirmed dispatch_log schema |
| src/mock_app.py | Standalone FastAPI app - login, RBAC routes, evidence log, alert trigger |
| src/evidence_ui.html | Standalone evidence documentation UI (local prototype, no backend yet) |
| src/test_security.py | Automated pytest suite (19 tests) for all security modules |
| requirements.txt | Python dependencies for the security module |

## Testing

Run the automated test suite:

    cd security/src
    pytest test_security.py -v

19 tests covering PII masking, password security, RBAC, jurisdiction
scoping, alert dispatch, dispatch log DB writes, and evidence
log/alert-trigger endpoint authorization. All passing as of last run.

## Confirmed Backend Contract (from Kartike)

- POST /api/auth/login - request: username, password. Response 200:
  access_token, token_type, role, expires_in. Response 401: detail.
- JWT payload: sub, role, jurisdiction, exp. Jurisdiction claim
  confirmed present (e.g. "New Delhi") - no backend change needed.
- Roles (DB column users.role, VARCHAR): admin, cyber_cell_officer,
  bank_nodal_officer.

## Pending

- Real backend integration - awaiting backend URL/access from
  Kartike (LAN via --host 0.0.0.0) to test against the live
  /api/auth/login endpoint.
- Production DB wiring - swap SQLite connection for the real
  Postgres dispatch_log table once backend access is available.
- Alert Dispatch and WebSocket Security (4th channel, /ws/alerts) -
  on hold, awaiting confirmation from Kartike on the authentication
  approach.
- PII masking - confirming with Kartike whether the masking in
  complaints.py was written by him or was already present, to
  avoid duplicating pii_masking.py in production.
- Evidence documentation UI is currently local-only (browser
  localStorage); needs to be wired to the /evidence-log endpoint
  once the real backend is available.

## Dispatch Log DB

dispatch_db.py implements the confirmed schema (id, complaint_id,
channel, recipient, dispatched_at, delivery_status, raw_response)
matching app/models/complaint.py -> DispatchLog. Currently backed by
SQLite for local testing; swapping to production Postgres only
requires a connection-string change.
