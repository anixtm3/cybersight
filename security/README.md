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
authorization implemented and tested, ready for the jurisdiction
JWT claim once added by the backend team. Full backend integration
(real login endpoint, dispatch_log table) is in progress pending
backend URL/access and dispatch_log schema from Kartike.

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
| src/alert_dispatch.py | Mocked multi-channel alert dispatch (SMS, email, webhook) |
| src/mock_app.py | Standalone FastAPI app - login, RBAC routes, evidence log, alert trigger |
| src/evidence_ui.html | Standalone evidence documentation UI (local prototype, no backend yet) |
| src/test_security.py | Automated pytest suite (19 tests) for all security modules |
| requirements.txt | Python dependencies for the security module |

## Testing

Run the automated test suite:

    cd security/src
    pytest test_security.py -v

19 tests covering PII masking, password security, RBAC, jurisdiction
scoping, alert dispatch, and evidence log/alert-trigger endpoint
authorization. All passing as of last run.

## Confirmed Backend Contract (from Kartike)

- POST /api/auth/login - request: username, password. Response 200:
  access_token, token_type, role, expires_in. Response 401: detail.
- JWT payload: sub, role, exp (jurisdiction claim pending).
- Roles (DB column users.role, VARCHAR): admin, cyber_cell_officer,
  bank_nodal_officer.

## Pending

- Real backend integration - awaiting backend URL/access from
  Kartike to test against the live /api/auth/login endpoint.
- dispatch_log table schema - needed to wire alert_dispatch.py to
  the real database, replacing the current placeholder entries.
- jurisdiction JWT claim - backend team to add jurisdiction_district
  to the token; require_jurisdiction() in rbac.py is ready and tested.
- Alert Dispatch and WebSocket Security (4th channel, /ws/alerts) -
  on hold, awaiting confirmation from Kartike on the authentication
  approach.
- PII masking duplication check - confirming with Kartike whether
  masking already present in complaints.py is separate from this
  module, to avoid duplicate implementation.
- Evidence documentation UI is currently local-only (browser
  localStorage); needs to be wired to the /evidence-log endpoint
  once the real backend is available.
