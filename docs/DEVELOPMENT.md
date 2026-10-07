# Development

> Owner: Engineering maintainers  
> Update when: local setup, CI, PR, or development workflow changes  
> Last Updated: 2026-10-08  
> Do NOT put here: production secrets

## Repository workflow

Use `main` for explicitly authorized direct work. Keep changes scoped and update canonical docs when architecture/status changes.

## Application structure

- `web-platform/frontend`: Next.js frontend.
- `web-platform/backend`: FastAPI backend.
- `web-platform/backend/tests`: backend tests.
- `web-platform/frontend/e2e`: Playwright E2E.
- `web-platform/backend/alembic`: migrations.

## Development principles

- Mock-first integration boundaries are valid for local development.
- Real providers must remain explicit adapters.
- Do not add a second worker application.
- Local workers use the repository's canonical backend worker code.
- Never commit `.env` secrets.

## Validation

Applicable checks include:
- backend unit/integration tests;
- frontend typecheck/build;
- frontend tests where configured;
- Playwright E2E;
- lint/security tooling where configured.

Docs-only commits intentionally may not trigger code CI. Fresh CI/security evidence is required on the next code-changing release SHA.

## PR/CI rules

PR validation should remain active. Full validation can be triggered through the repository's workflow-dispatch mechanism when configured. Do not treat a documentation-only workflow result as evidence that code paths were tested.

## Documentation

When a code change alters behavior, update the appropriate canonical domain document and CURRENT_STATE/ROADMAP when status or gates change.
