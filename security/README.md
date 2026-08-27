# Security Module - CyberSight

**Developer:** Kanav Agarwal
**Role:** Security Engineer
**Branch:** kanav

This folder documents the security design for CyberSight - covering
authentication, authorization, rate limiting, PII protection, and
audit logging.

## Status

Day 1 - Security foundation and design documented. Core logic
(PII masking, rate limiting, RBAC, password security, alert
dispatch, audit logging) implemented and independently tested
using a standalone mock environment plus an automated pytest
suite. Full backend integration is pending confirmation of the
API contract (user model, JWT payload structure, and route
definitions) from the backend team.

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
| 11-testing-evidence.md | Independent testing evidence (PII masking, RBAC, rate limiting, pytest suite) |

## Code

| File | Covers |
|---|---|
| src/pii_masking.py | Phone, email, account, Aadhaar, PAN, address masking functions |
| src/rate_limiter.py | In-memory rate limiter (5 attempts / 60 seconds) |
| src/rbac.py | JWT token creation, decoding, and role-based access dependency |
| src/audit_log.py | JSON-lines audit event logger |
| src/password_security.py | Password hashing and verification using bcrypt |
| src/alert_dispatch.py | Mocked multi-channel alert dispatch (SMS, email, webhook) |
| src/mock_app.py | Standalone FastAPI app used to independently test the above |
| src/test_security.py | Automated pytest suite for all security modules |

## Testing

Run the automated test suite:

    cd security/src
    pytest test_security.py -v

12 tests covering PII masking, password security, RBAC token
creation, and alert dispatch. All passing as of last run.

## Pending

- Section 11 (backend integration) - full end-to-end testing against
  the real backend, awaiting confirmed auth contract from Kartike/Saina.
- Alert Dispatch and WebSocket Security - on hold, awaiting confirmation
  from Kartike on the /ws/alerts authentication approach.
