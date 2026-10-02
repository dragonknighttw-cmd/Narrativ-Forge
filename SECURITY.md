# Security Policy

Narrativ Forge is a private, invite-only production workspace. Security-sensitive behavior is treated as a first-class implementation concern.

## Current foundation

- Authentication is currently a development-only session skeleton.
- Workspace sessions use an httpOnly cookie; client-side localStorage is not used for auth tokens.
- Backend authorization has a reusable role guard.
- CORS is configured through an explicit allowlist.
- Secrets and environment-specific credentials belong in `.env`, not Git.
- Google OAuth, production session management, upload hardening, audit logging, and Drive export security are deferred to their respective integration/hardening phases.

## Reporting

For a security issue in a deployed instance, report it privately to the project maintainer rather than opening a public issue with exploit details.

Do not include passwords, OAuth tokens, private media, or other credentials in reports.

## Scope note

The current Phase 1 development authentication is not production-ready. Production deployment must not rely on the default development credentials or development session behavior.
