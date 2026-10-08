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


## Pre-staged continuation queue — 2026-10-08

Independent implementation work is now intentionally staged so the next work can continue without redesigning the execution order.

### Phase 15 — Cross-platform export preparation
- Normalize platform metadata, title/caption/hashtag constraints, scheduled-time validation, and idempotent preparation keys.
- Keep direct publishing disabled; output preparation manifests only.
- Gate: representative export manifests + UI state coverage.

### Phase 16 — Trend integration adapter
- Connector interface, cache/TTL, rate-limit fallback, attribution fields, and provider-specific adapters.
- Gate: live connector limits/terms and sample data quality.

### Phase 17 — A/B testing + feedback loop
- Experiment registry, allocation validation, minimum sample guardrails, winner selection, and review-learning ingestion.
- Gate: real analytics/event data and owner approval before automated decisions.

### Phase 18 — Publishing metadata/idempotency
- Durable preparation ledger, retry-safe metadata generation, duplicate prevention, and recovery states.
- Gate: persistence-backed duplicate/retry E2E.

### Phase 19 — Trend connectors
- Provider adapters, quota accounting, cache invalidation, attribution, and fallback routing.
- Gate: account/API credentials and provider terms.

### Phase 20 — Experiment registry
- Persistent experiment/variant/outcome schema, audit history, allocation constraints, and stop/winner controls.
- Gate: analytics source verification.

### Phase 21 — AI quality evaluation/provider ranking
- Stable evaluation cases, provider scoring, latency/cost/quality dimensions, and regression snapshots.
- Gate: representative Burmese dataset + live provider measurements.

### Phase 22 — EDL/FCPXML/NLE manifests
- Timeline validation, overlap detection, deterministic manifests, and export metadata.
- Gate: import validation in target NLEs.

### Phase 23 — Storage lifecycle/DR
- Hot/cold/archive policy, retention safety for final/referenced assets, replica reconciliation, backup verification, and restore drill automation.
- Gate: real storage + isolated restore evidence.

### Phase 24 — SRE/incident/compliance foundations
- Alert rules, incident events, runbook hooks, evidence references, and compliance checklist tracking.
- Gate: live alert delivery + incident drill.

### Phase 25 — Character/style bible
- Character profiles, style profiles, continuity constraints, and reusable production context.
- Gate: real series acceptance dataset.

### Phase 26 — Hook recommendation/episode scoring
- Eight hook families, deterministic ranking, retention/continuity/cost scoring, and explainable recommendations.
- Gate: human evaluation dataset.

### Phase 27 — Burmese subtitle evaluation
- Timing/unicode/line-length/overlap scoring, correction history, and evaluation exports.
- Gate: representative Burmese subtitle corpus.

### Phase 28 — Selective regeneration
- Dependency graph, affected-output calculation, invalidation/preservation plan, and safe partial regeneration.
- Gate: persistence-backed regeneration E2E.

### Phase 29 — Quota-aware scheduling
- Provider quota reservation, idempotency keys, warning/fallback thresholds, and batch planning.
- Gate: live provider quota measurements.

### Phase 30 — Human-review learning
- Review decision events, issue frequency, quality scores, and explainable feedback summaries.
- Gate: privacy/data-retention approval.

### Phase 31 — Collaboration seam
- Shared resource permissions, optimistic locking, audit trails, and conflict states.
- Gate: multi-user concurrency E2E.

### Phase 32 — Realtime notifications/presence
- Presence contracts, event fan-out seam, reconnect state, and notification delivery abstraction.
- Gate: live realtime provider/runtime load test.

### Phase 33 — Usage quotas
- Per-tenant usage accounting, quota enforcement, idempotent reservations, and admin visibility.
- Gate: billing/plan mapping.

### Phase 34 — Enterprise tenant policy
- Storage/concurrency/role policy validation and organization-level policy enforcement.
- Gate: enterprise acceptance matrix.

### Phase 35 — Demo/onboarding/support seam
- Deterministic demo seed, onboarding states, support diagnostics, safe redaction, and troubleshooting evidence bundle.
- Gate: fresh-user browser E2E.

### Phase 36 — Launch gate / pen-test remediation
- Consolidate all release evidence, remediate scan/pen-test findings, freeze release SHA, and produce final acceptance record.
- Gate: all applicable release gates VERIFIED or explicitly waived by owner.

### Execution rule for the continuation queue

Phases 15–35 can be implemented/tested in parallel where dependencies permit. Live provider, billing, legal, security, and external acceptance gates remain separate. No new Git branch is required for this queue; implementation continues on main as requested.
