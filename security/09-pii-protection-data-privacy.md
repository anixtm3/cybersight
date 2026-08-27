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


