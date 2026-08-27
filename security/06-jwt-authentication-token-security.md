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
- role — exact application role
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

