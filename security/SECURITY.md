# CyberSight — Security Engineering

**Developer:** Kanav Agarwal  
**Role:** Security Engineer  
**Project:** CyberSight — Cybercrime Prediction System  
**Branch:** kanav

---

## 1. Security Objective

The CyberSight security layer protects sensitive cybercrime complaint,
investigation, financial, intelligence, and alert-related data.

The security design focuses on:

- Authentication
- Authorization
- Jurisdiction-scoped access control
- Token security and revocation
- Rate limiting
- PII protection
- Audit logging
- Secure alert delivery
- WebSocket security

---

## 2. Day 1 Scope

Day 1 establishes the security foundation and defines the integration
contracts required by the CyberSight backend and frontend.

### Security Components

1. JWT authentication
2. Refresh-token handling
3. Token revocation
4. Role-based access control
5. Jurisdiction-scoped authorization
6. API rate limiting
7. PII masking
8. Security audit logging
9. Alert-dispatch security
10. WebSocket authentication

---

## 3. Security Principles

### Least Privilege

Users receive only the permissions required for their role and
jurisdiction.

### Deny by Default

Requests are rejected unless authentication, role authorization,
jurisdiction authorization, and resource authorization succeed.

### Defense in Depth

Multiple security controls are applied instead of relying on a
single authentication mechanism.

### Secure Secret Handling

Secrets must not be hard-coded or committed to the repository.

### Auditability

Security-sensitive operations must generate auditable events.

### Data Minimization

Sensitive and personally identifiable information should only be
exposed when operationally required.

---

## 4. Current Integration Decisions

The following items require confirmation from the backend integration
owner before implementation is finalized.

### WebSocket Authentication

Decision: PENDING

Question:

Should /ws/alerts require JWT authentication from Day 1, or remain
temporarily open for development/testing?

### RBAC Role Names

Decision: PENDING

Proposed role identifiers:

- i4c_admin
- cybercell_officer
- ank_nodal_officer

These exact strings must be confirmed before they are used in JWT
claims and authorization checks.

---

## 5. Day 1 Status

Security foundation initialized.

Implementation and integration decisions will be finalized after
backend contract confirmation.
---

## 6. JWT Authentication & Token Security

### Authentication Model

CyberSight uses JSON Web Tokens (JWT) for authenticated API access.

The authentication flow is:

User Login
    |
    v
Credential Verification
    |
    v
JWT Access Token + Refresh Token
    |
    v
Protected API Request
    |
    v
JWT Validation
    |
    v
Authorization

### Access Token

The access token is used for authenticated API requests.

Required JWT claims:

- sub — authenticated user identifier
- 
ole — exact application role
- jurisdiction — authorized jurisdiction
- iat — token issued-at timestamp
- exp — token expiration timestamp
- jti — unique token identifier

### Refresh Token

Refresh tokens are used to obtain new access tokens without requiring
the user to authenticate again.

Refresh tokens must:

- Have a separate expiration period
- Be securely stored
- Be associated with the authenticated user
- Be revocable
- Not be exposed unnecessarily to frontend code or logs

### Token Revocation

Each token must have a unique jti.

When a token is explicitly revoked, its jti must be recorded in the
token-revocation store.

Protected requests must verify:

1. JWT signature
2. Token expiration
3. Token issuer/audience where configured
4. Token jti
5. Revocation status
6. Required role
7. Jurisdiction authorization

A revoked token must be rejected even if its cryptographic signature
and expiration are otherwise valid.

### Logout

Logout invalidates the active token/session according to the
revocation strategy.

Logout must also generate an audit event.

### Password Security

Passwords must never be stored in plaintext.

Password verification and storage must use bcrypt hashing.

### Secret Management

The JWT signing secret must be supplied through secure environment
configuration.

The signing secret must never be committed to Git.

### JWT Security Requirements

- Use a strong signing secret.
- Use an explicitly configured signing algorithm.
- Keep access tokens short-lived.
- Validate expiration.
- Validate token identifiers.
- Check revocation status.
- Never trust client-supplied role or jurisdiction values.
- Do not log complete JWTs.
- Do not expose secrets in error responses.

### Current Status

JWT authentication design documented.

Implementation depends on confirmation of the backend authentication
contract and exact RBAC role identifiers.
---

## 7. RBAC & Jurisdiction-Scoped Authorization

### Authorization Model

CyberSight uses role-based access control (RBAC) combined with
jurisdiction-scoped authorization.

Authentication establishes the identity of the requester.

Authorization determines whether that authenticated user may perform
the requested operation on the requested resource.

Authorization must be enforced server-side.

### Role Identifiers

The final role identifiers are currently pending backend-team
confirmation.

Proposed identifiers:

- i4c_admin
- cybercell_officer
- ank_nodal_officer

The exact confirmed strings must be used consistently in:

- JWT 
ole claims
- Backend authorization checks
- Database role records
- Frontend role checks
- Security documentation

### Jurisdiction Scoping

Role authorization alone is insufficient for operational data access.

A user's permitted jurisdiction must also be evaluated before access
to jurisdiction-sensitive resources is granted.

Examples of jurisdiction-sensitive resources include:

- Cybercrime complaints
- Cases
- Alerts
- Evidence
- Intelligence records
- Prediction results
- Investigation information

### Authorization Flow

Request
   |
   v
JWT Validation
   |
   v
Token Revocation Check
   |
   v
Role Authorization
   |
   v
Jurisdiction Authorization
   |
   v
Resource Authorization
   |
   +---- ALLOW ----> Requested Operation
   |
   +---- DENY -----> 403 Forbidden

### Deny-by-Default

Access must be denied when:

- Authentication is missing
- JWT is invalid
- JWT is expired
- JWT has been revoked
- Required role is missing
- Jurisdiction information is missing
- Requested resource is outside the user's permitted jurisdiction
- Required permission is not available

### Client Input Security

The backend must never trust client-provided values for:

- Role
- User identity
- Jurisdiction
- Authorization scope

These values must be derived from trusted authentication and
server-side authorization data.

### Authorization Audit

Authorization failures must generate security audit events.

Sensitive successful operations should also be auditable according
to the audit-logging policy.

### Current Status

RBAC and jurisdiction-scoping model documented.

Final role identifiers remain pending backend-team confirmation.
---

## 8. Rate Limiting & API Abuse Protection

### Objective

Rate limiting protects CyberSight APIs from excessive requests,
brute-force attempts, automated abuse, and denial-of-service-style
request floods.

Rate limiting must be enforced server-side.

### Protected Areas

Rate limiting should be applied with higher priority to:

- Authentication endpoints
- Login attempts
- Token refresh endpoints
- Password-related endpoints
- Alert-dispatch endpoints
- Sensitive data-access endpoints
- Administrative endpoints
- Publicly reachable API endpoints

### Authentication Protection

Repeated failed authentication attempts must be rate-limited to
reduce credential-guessing and brute-force attacks.

### Request Limits

The exact production limits will be finalized during backend
integration based on endpoint sensitivity and deployment capacity.

The rate-limiting configuration must be environment-controlled
rather than hard-coded into individual endpoints.

### Rate-Limit Response

When a request exceeds its configured limit, the API should return
an appropriate HTTP rate-limit response.

The response should not disclose sensitive implementation details.

### Monitoring

Rate-limit violations should be available for security monitoring
and may generate audit/security events for repeated or suspicious
activity.

### Fail-Safe Behavior

Rate limiting must not bypass authentication or authorization.

A request that passes the rate limiter must still pass:

1. JWT validation
2. Token revocation checks
3. Role authorization
4. Jurisdiction authorization
5. Resource authorization

### Configuration Requirements

Rate-limit configuration should support:

- Enable/disable control by environment
- Per-endpoint limits
- Authentication-specific limits
- Configurable request windows
- Production-safe defaults

### Current Status

Rate-limiting security requirements documented.

Exact endpoint limits remain pending backend implementation and
deployment configuration.
---

## 9. PII Protection & Data Privacy

### Objective

CyberSight processes sensitive cybercrime, identity, financial,
investigation, and intelligence-related information.

PII and other sensitive information must only be exposed when
operationally required.

### Sensitive Information

Security controls must be considered for information including:

- Personally identifiable information
- Contact information
- Account information
- Financial information
- Transaction information
- Investigation-related information
- Evidence-related information
- Other sensitive complaint data

### Data Minimization

Only the minimum information required for an authorized operation
should be returned to clients, displayed in dashboards, or included
in notifications.

### PII Masking

Sensitive values should be masked when their complete value is not
required.

Examples:

- Phone numbers should expose only the minimum required digits.
- Email addresses should be partially masked where appropriate.
- Account numbers should not be exposed in full unless operationally
  required.
- Other sensitive identifiers should follow the same minimization
  principle.

### API Response Protection

API responses must not expose unnecessary PII.

Authorization must be performed before returning sensitive records.

A valid JWT alone does not grant unrestricted access to sensitive
information.

### Logging Protection

Sensitive PII, credentials, JWTs, refresh tokens, and secrets must
not be written to application logs in plaintext.

Security logs should contain enough information for investigation
without unnecessarily reproducing sensitive data.

### Notification Protection

SMS, email, webhook, and dashboard notifications should contain only
the information necessary for the recipient to understand and act on
the alert.

Sensitive information should not be included unnecessarily in
notification payloads.

### Storage Protection

Sensitive information must be protected through appropriate database
access controls and application-level authorization.

Encryption requirements must follow the project's approved backend
and database security architecture.

### Transport Protection

Sensitive information must be transmitted only through authenticated
and appropriately secured communication channels.

### Access Control

Access to sensitive information must be evaluated using:

1. Authentication
2. Role authorization
3. Jurisdiction authorization
4. Resource-level authorization

### PII Auditability

Sensitive-data access should be auditable where required by the
security and investigation workflows.

### Current Status

PII protection requirements documented.

Detailed field-level masking rules will be finalized after the
backend data schema is confirmed.

---

## 10. Audit Logging & Security Events

### Objective

CyberSight must maintain an auditable record of security-sensitive
and investigation-relevant actions.

Audit logging supports:

- Security monitoring
- Incident investigation
- Accountability
- Detection of unauthorized activity
- Investigation traceability

### Events to Audit

The security audit layer should record events including:

#### Authentication

- Successful login
- Failed login
- Logout
- Token refresh
- Token revocation

#### Authorization

- Authorization failure
- Role validation failure
- Jurisdiction validation failure
- Unauthorized resource access attempt

#### Sensitive Data Access

- Sensitive complaint access
- Case access
- Evidence access
- Intelligence access
- Sensitive PII access

#### Alert Operations

- Alert creation
- Alert dispatch
- Alert acknowledgement
- Alert escalation
- Alert status changes

#### Administrative Operations

- User creation
- User modification
- Role modification
- Jurisdiction assignment changes
- Security configuration changes

### Recommended Audit Fields

Each audit event should contain sufficient information to establish
who performed an action, what happened, when it happened, and the
result.

Recommended fields:

- event_id
- event_type
- actor_user_id
- actor_role
- jurisdiction
- resource_type
- resource_id
- action
- status
- timestamp
- ip_address
- user_agent
- request_id
- failure_reason

Sensitive values such as passwords, JWTs, refresh tokens, and secrets
must never be stored in audit logs.

### Authentication Audit Example

```text
event_type: AUTH_LOGIN
actor_user_id: user-001
action: LOGIN
status: SUCCESS
timestamp: <server timestamp>
request_id: <request identifier>
```

### Authorization Failure Example

```text
event_type: AUTHORIZATION_DENIED
actor_user_id: user-001
actor_role: <role>
jurisdiction: <jurisdiction>
resource_type: CASE
resource_id: <resource identifier>
action: READ
status: DENIED
failure_reason: JURISDICTION_MISMATCH
timestamp: <server timestamp>
```

### Alert Dispatch Audit

Each alert dispatch should record the outcome of the individual
delivery channels.

The four supported channels are:

- SMS
- Email
- Webhook
- Dashboard

Per-channel status fields:

- sms_status
- email_status
- webhook_status
- dashboard_status

Suggested channel status values:

- PENDING
- SENT
- DELIVERED
- FAILED

If an overall dispatch status is required, it may be represented
separately as:

- PENDING
- PARTIAL
- SUCCESS
- FAILED

The individual channel statuses remain the source of truth.

### Log Security

Audit logs must:

- Avoid storing credentials
- Avoid storing complete JWTs
- Avoid storing refresh tokens
- Avoid storing unnecessary PII
- Restrict unauthorized modification
- Be protected from unauthorized access
- Preserve event timestamps
- Preserve event ordering where required

### Audit Integrity

Audit records should be append-oriented.

Normal application users must not be able to modify or delete
security audit events.

### Monitoring

Repeated authentication failures, authorization failures, unusual
access patterns, and repeated rate-limit violations should be
available for security monitoring.

### Current Status

Audit logging requirements documented.

Final database schema and implementation will be aligned with the
backend database design.