# Phase 1 — Foundation Exit Checklist

## Repository and architecture

- [x] Root structure separated from application code
- [x] Frontend/backend/docs/mobile boundaries created
- [x] Next.js frontend shell created
- [x] FastAPI backend created
- [x] SQLite + PostgreSQL-compatible ORM foundation created
- [x] Heavy-work boundary kept outside the API/frontend
- [x] Mock-first integration boundary documented

## Access and security foundation

- [x] Invite-only development login boundary
- [x] Backend authentication dependency
- [x] Reusable backend role guard
- [x] httpOnly session cookie
- [x] No client-side token storage
- [x] CORS origin allowlist
- [x] Environment examples separated from source code
- [x] Production secrets/OAuth deferred until the appropriate hardening/integration phase

## Application shell

- [x] Protected workspace shell
- [x] Login loading/error states
- [x] Session-check loading state
- [x] Responsive base layout
- [x] Foundation dashboard without fake production metrics
- [x] Reserved routes for later workflow modules

## API and verification

- [x] Health endpoint
- [x] Login/logout/me endpoints
- [x] Ideas API skeleton
- [x] Episodes API skeleton
- [x] Backend foundation test suite added
- [x] Frontend typecheck command added
- [ ] Real local dependency installation + test/build execution
- [ ] CI execution of backend tests and frontend typecheck

The last two items are environment/CI verification gates rather than code-completion blockers; this environment does not provide a connected local checkout/runtime for the repository.

## Phase 2 entry condition

Do not add real media, AI, Google Drive, or production storage integrations yet.

Next: build Ideas → Series → Seasons → Episodes as a complete vertical slice:

`DB → API → UI → validation → empty/loading/error states → tests`
