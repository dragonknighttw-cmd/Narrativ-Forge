# Narrativ Forge — Phase Execution & Evidence Plan

This is the implementation queue for work that can be completed without production credentials. A phase is not marked VERIFIED until its required evidence exists.

## Active parallel tracks

### Track A — Worker / processing
- Phase 1: real worker CI evidence — fix CI failures, rerun, then verify real Docker/Celery/Redis/PostgreSQL/FFmpeg/Whisper path.
- Phase 3: retry/DLQ/recovery — keep PostgreSQL concurrency tests and failure recovery in the CI gate.

### Track B — Media / storage / AI
- Phase 2: real-media E2E — automated local evidence first; live provider evidence later.
- Phase 4: storage lifecycle — local provider checksum/path-safety/resumable tests are automated; B2/Supabase/Cloudinary live lifecycle remains a credential gate.
- Phase 5: transcription — keep local Whisper CLI evidence; Cloudflare Whisper/fallback and Burmese quality remain a live gate.
- Phase 6: Google Drive export — OAuth/token/Drive live verification remains a credential gate.
- Phase 7: notifications — SMTP live delivery remains a credential gate.
- Phase 8: billing — Stripe webhook/idempotency/live payment verification remains a credential gate.

### Track C — Production hardening
- Phase 9: auth/tenant isolation — cross-tenant series access regression coverage is prepared; broader resource-by-resource isolation and live auth remain gates.
- Phase 10: backup/restore — non-destructive pg_restore archive verification tooling is prepared; staging restore drill remains a gate.
- Phase 11: observability — Prometheus/structured logging/Sentry hooks exist and security/observability regression coverage is prepared; live Sentry delivery remains a credential gate.
- Phase 12: security — CodeQL/Security CI plus upload/path and security-header/runtime regression coverage are prepared; webhook/provider live checks remain.
- Phase 13: performance — bounded HTTP load probe is prepared; real worker/queue load testing remains a final staging gate.
- Phase 14: accessibility/UX/legal/provider terms — final acceptance gate.

## Credential batch (deferred until code/evidence work is exhausted)

Collect only when needed: production database/Redis, storage provider credentials, Cloudflare Whisper auth, Google OAuth, SMTP, Stripe, Sentry, and production frontend/API settings. Never commit secrets.

## Release rule

Production Ready requires green CI, a continuously provisioned worker runtime, live provider verification, backup/restore evidence, tenant isolation evidence, security/performance evidence, and final manual acceptance. Prepared foundations are not equivalent to VERIFIED.
