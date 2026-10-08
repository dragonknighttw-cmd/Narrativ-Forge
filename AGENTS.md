# Narrativ Forge — OpenCode Project Instructions

## Mission

You are working inside Narrativ Forge, a private, invite-only Burmese short-form video production workspace. When asked to implement a change, inspect the existing implementation first and make the smallest complete change in the repository rather than only explaining what the user should do.

## Required reading order

Before substantial work, read:
1. `README.md`
2. `CURRENT_STATE.md`
3. `ROADMAP.md`
4. `TOOL.md`
5. The relevant domain document under `docs/`
6. Relevant source code and tests

For UI work also read `UI_DESIGN_SYSTEM.md`.
For security-sensitive work also read `SECURITY.md`.

## Repository map

- `web-platform/frontend`: Next.js + React + TypeScript frontend.
- `web-platform/backend`: FastAPI + SQLAlchemy backend.
- `web-platform/backend/tests`: backend tests.
- `web-platform/frontend/e2e`: Playwright E2E.
- `web-platform/backend/alembic`: database migrations.
- `web-platform/backend/app/workers`: canonical Celery worker path.
- `.github/workflows/`: CI, security, CodeQL, worker evidence, and repository gate workflows.

## Architecture rules

- Preserve the existing Next.js/FastAPI/PostgreSQL/Redis/Celery architecture.
- Do not create a second worker implementation.
- Keep AI providers behind existing adapters/routing.
- Keep storage routing behind the existing storage abstraction.
- Human approval remains mandatory before final export.
- Google Drive is an approved-output destination, not the workflow database.
- Do not add direct TikTok/YouTube/Facebook/Instagram publishing.
- Prefer existing UI primitives and design tokens; do not introduce a parallel UI framework without an explicit architecture decision.

## Security rules

- Never add, print, hard-code, or commit credentials, tokens, cookies, private keys, or provider secrets.
- Never read or modify real `.env` files as part of normal repository work.
- Preserve tenant isolation and server-side authorization.
- Do not bypass upload, webhook, OAuth, provider watermark, commercial-use, or human-approval safeguards.
- Do not delete or overwrite approved/original media without an explicit requirement.

## Git rules

- Work directly on `main` when the user explicitly asks for direct repository changes.
- Keep commits logically scoped.
- Do not push changes automatically.
- Before committing, inspect the diff and relevant tests.
- Never use a green local/unit result to claim production or provider verification.

## Implementation workflow

1. Inspect the relevant files and current behavior.
2. Identify the smallest complete implementation.
3. Edit the existing code rather than duplicating functionality.
4. Add or update focused tests when behavior changes.
5. Run the narrowest useful checks first.
6. Run broader checks when practical.
7. Inspect the final diff.
8. Update canonical documentation only when behavior, architecture, requirements, or evidence status actually changes.
9. Report exactly what was changed and what was/was not verified.

## Validation commands

Frontend:
- `cd web-platform/frontend && npm run typecheck`
- `cd web-platform/frontend && npm run build`
- `cd web-platform/frontend && npm run e2e`

Backend:
- `cd web-platform/backend && pytest`
- `cd web-platform/backend && pytest -m unit`

Use the repository's existing CI workflows for integration, security, CodeQL, and real-worker evidence. Do not invent a passing result when a dependency/runtime is unavailable.

## Evidence language

Use these meanings consistently:
- DONE: implemented in the repository.
- VERIFY: implementation exists but fresh evidence is required.
- VERIFIED: fresh environment/provider evidence exists.
- PENDING: work/evidence has not been completed.
- BLOCKED: a concrete dependency prevents verification.
- EXTERNAL ACTION: requires an owner, provider, legal/security reviewer, or external system.

Configuration, credentials, source code, and unit tests alone do not prove live provider health.

## Working style

- Prefer direct implementation over lengthy instructions.
- Reuse existing abstractions and conventions.
- Avoid speculative rewrites.
- Preserve backwards compatibility unless the task explicitly requires a breaking change.
- When uncertain about a destructive or externally visible action, stop and ask for confirmation.
