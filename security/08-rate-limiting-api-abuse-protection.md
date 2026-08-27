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

