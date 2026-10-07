# Security Policy

> Owner: Project maintainers  
> Update when: security controls, threats, incidents, or verification gates change  
> Last Updated: 2026-10-08  
> Do NOT put here: credentials or private provider values

Narrativ Forge is a private, invite-only production workspace. Security-sensitive behavior is a first-class implementation concern.

## Security boundary

- Backend owns database access.
- Frontend must never receive service-role database credentials.
- Authentication/session state is server-controlled.
- CORS/trusted-host policies are explicit.
- Tenant/resource authorization is enforced server-side.
- RLS is defense-in-depth where configured.
- OAuth material is stored server-side and encrypted where required.
- Production credentials belong in protected deployment configuration, never Git.
- Webhook inputs require HTTPS/SSRF protections.
- Upload MIME, extension, size, filename, and path safety are enforced server-side.
- Original assets and approved outputs must not be overwritten or blindly deleted.

## AI security

- AI provider credentials remain backend-only.
- Backend AI gates are authoritative.
- Public AI is disabled by default where configured.
- Human approval remains required before final export/publication preparation.
- Provider watermark/commercial-use restrictions must not be bypassed.

## Current verification state

Security implementation foundations are present, including session controls, CORS/trusted-host validation, upload hardening, webhook protections, tenant scoping, audit-event scoping, protected configuration, and security-test foundations.

Still required for release:
- fresh security/dependency/container scans on the release SHA;
- production auth and cross-tenant E2E;
- credential rotation drill;
- accessibility/security review;
- external penetration testing;
- legal/privacy review.

## Incident reporting

Report security issues privately to the project maintainer. Do not publish credentials, private media, session cookies, OAuth tokens, or other sensitive values in issues, logs, tickets, or chat.

## Ownership

Deployment procedures belong in `docs/DEPLOYMENT.md`. Operational rotation/recovery belongs in `docs/OPERATIONS.md`. API security behavior belongs in `docs/API.md`.
