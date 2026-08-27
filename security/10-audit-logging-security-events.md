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