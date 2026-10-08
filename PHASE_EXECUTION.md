# Narrativ Forge — Phase Execution & Evidence Plan

This is the implementation queue for work that can be completed without production credentials. A phase is not marked VERIFIED until its required evidence exists.

## Active parallel tracks

### Track A — Worker / processing
- Phase 1: real worker CI evidence — fix CI failures, rerun, then verify real Docker/Celery/Redis/PostgreSQL/FFmpeg/Whisper path.
- Phase 3: retry/DLQ/recovery — keep PostgreSQL concurrency tests and failure recovery in the CI gate.

### Track B — Media / storage / AI
- Phase 2: real-media E2E — automated local evidence first; live provider evidence later.
- Phase 4: storage lifecycle — local provider safety/resumable tests are automated; B2/Supabase/Cloudinary live lifecycle remains a credential gate.
- Phase 5: transcription — keep local Whisper CLI evidence; Cloudflare Whisper/fallback and Burmese quality remain a live gate.
- Phase 6: Google Drive export — OAuth/token/Drive live verification remains a credential gate.
- Phase 7: notifications — SMTP live delivery remains a credential gate.
- Phase 8: billing — Stripe webhook/idempotency/live payment verification remains a credential gate.

### Track C — Production hardening
- Phase 9: auth/tenant isolation — add automated cross-tenant authorization coverage before live acceptance.
- Phase 10: backup/restore — provide non-destructive archive verification and a staging restore procedure; never call production restore automatically.
- Phase 11: observability — retain Prometheus/structured logging hooks and add CI assertions where possible; Sentry live delivery remains a credential gate.
- Phase 12: security — CodeQL/Security CI is evidence; add targeted regression tests for upload/path/webhook boundaries.
- Phase 13: performance — use the bounded load probe against staging/CI, then perform real worker/queue load testing as a final gate.
- Phase 14: accessibility/UX/legal/provider terms — final acceptance gate.

## Credential batch (deferred until code/evidence work is exhausted)

Collect only when needed: production database/Redis, storage provider credentials, Cloudflare Whisper auth, Google OAuth, SMTP, Stripe, Sentry, and production frontend/API settings. Never commit secrets.

## Release rule

Production Ready requires green CI, a continuously provisioned worker runtime, live provider verification, backup/restore evidence, tenant isolation evidence, security/performance evidence, and final manual acceptance. Prepared foundations are not equivalent to VERIFIED.
