# Security Module - CyberSight

**Developer:** Kanav Agarwal
**Role:** Security Engineer
**Branch:** kanav

This folder documents the security design for CyberSight - covering
authentication, authorization, rate limiting, PII protection, and
audit logging.

## Status

Day 1 - Security foundation and design documented. Implementation
is pending confirmation of the backend API contract (user model,
JWT payload structure, and route definitions) from the backend team.

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

## Pending

- Section 11 - Alert Dispatch and WebSocket Security: on hold, awaiting
  confirmation from Kartike on the /ws/alerts authentication approach.
