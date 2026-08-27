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

