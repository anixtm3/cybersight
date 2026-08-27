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


