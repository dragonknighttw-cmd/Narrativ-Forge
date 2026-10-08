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


## Post-36 continuation queue

After Phase 36, remaining work is staged as:

### Phase 37 — Release train / migration safety
- Release manifests, migration compatibility windows, rollback notes, and versioned deployment evidence.

### Phase 38 — Cost governance
- Provider cost ledger, budget alerts, per-tenant attribution, and anomaly thresholds.

### Phase 39 — Data lifecycle / privacy
- Retention classes, deletion workflows, export requests, redaction verification, and audit evidence.

### Phase 40 — Disaster recovery automation
- Restore-point selection, isolated restore orchestration, checksum validation, and recovery-time evidence.

### Phase 41 — Multi-region readiness
- Region capability matrix, data locality policy, failover routing, and degraded-mode behavior.

### Phase 42 — Advanced queue scheduling
- Priority classes, fair tenant scheduling, starvation prevention, backpressure, and capacity-aware admission.

### Phase 43 — Evaluation dataset governance
- Versioned Burmese evaluation sets, provenance, anonymization, regression baselines, and approval workflow.

### Phase 44 — Model/provider change management
- Provider/model registry versions, canary evaluation, rollback selection, and quality/cost regression gates.

### Phase 45 — Final operating maturity
- Quarterly DR/security drills, dependency review, incident postmortems, runbook freshness, and release-readiness audit.

Implementation rule remains: independent foundations may be developed in parallel on main; live credentials, external provider acceptance, legal/terms review, and manual browser/device acceptance stay as explicit gates.

## Post-36 implementation evidence map

The post-36 contracts are now implemented on `main` in
`web-platform/backend/app/services/operating_maturity.py`, with unit coverage in
`web-platform/backend/tests/test_operating_maturity.py`.

- **37 Release train:** `ReleaseManifest` + migration/rollback completeness validation.
- **38 Cost governance:** `CostObservation` + `CostPolicy` warning/critical classification.
- **39 Data lifecycle/privacy:** `RetentionClass` + deletion-request seam; evaluation datasets require anonymization.
- **40 Disaster recovery:** `RestorePoint`, `RestoreEvidence`, deterministic latest restore-point selection.
- **41 Multi-region:** capability/policy contracts and explicit failover eligibility.
- **42 Queue scheduling:** priority-class job contract and capacity-aware admission foundation.
- **43 Evaluation governance:** version/provenance/anonymization/baseline contract.
- **44 Model/provider change management:** versioned model comparison and canary quality regression guard.
- **45 Operating maturity:** dated drill contract with overdue-without-evidence detection.

These are **implementation foundations and automated unit evidence**, not live production verification. Provider billing, real backup/restore, regional failover, queue saturation, representative Burmese evaluation, and scheduled operational drills remain explicit acceptance gates.

## Next implementation queue — post-45

### Phase 46 — Evidence ledger
- Persist gate status, exact commit SHA, workflow run, artifact/evidence reference, owner, and verification timestamp.
- Prevent `VERIFIED` without attached evidence.

### Phase 47 — Provider acceptance matrix
- Track provider, credential dependency, quota/terms review, live test result, fallback, and commercial-use acceptance.
- Keep secrets outside the repository.

### Phase 48 — Production E2E rehearsal
- Execute the complete worker/media/retry/DLQ/storage/transcription/export pipeline against staging.
- Capture deterministic artifacts and rollback evidence.

### Phase 49 — Billing/entitlement reconciliation
- Reconcile Stripe plan state, tenant quotas, usage reservations, retries, webhook idempotency, and failure recovery.

### Phase 50 — Release candidate freeze
- Freeze release SHA, migration plan, environment manifest, rollback reference, evidence ledger, and acceptance checklist.

### Phase 51 — Final launch / post-launch watch
- Launch only after all applicable gates are VERIFIED or explicitly waived by owner.
- Run a bounded post-launch observation window and record incidents, rollback decision, and final sign-off.

**Rule:** 46–51 are intentionally pre-staged. They cannot honestly be marked VERIFIED until the corresponding live/manual evidence exists.

\n\n## Phase 46–51 implementation evidence — 2026-10-08\n\nThe post-45 queue is no longer documentation-only. Code, persistence models, migration, unit tests, and a repository-level release gate are now present on `main`.\n\n- **46 Evidence ledger:** `release_maturity.EvidenceLedgerEntry` + `evidence_ledger_entries`; VERIFIED requires exact 40-char commit SHA, workflow run, evidence reference, owner, and verification timestamp. WAIVED requires an explicit waiver reference. Database checks reject VERIFIED/WAIVED records without proof.\n- **47 Provider acceptance:** `ProviderAcceptance` + `provider_acceptance_records`; tracks credential dependency without storing secrets, quota/terms review, live result, fallback, commercial-use acceptance, and owner.\n- **48 Production E2E rehearsal:** `ReleaseCandidate`/watch contracts and the existing real-worker evidence workflow provide the release rehearsal seam; live staging execution remains blocked until the continuous worker runtime exists.\n- **49 Billing/entitlement reconciliation:** `BillingReconciliation` + `billing_reconciliation_records`; tenant quota/reservation/usage, webhook event uniqueness, and tenant/idempotency uniqueness are persisted.\n- **50 Release candidate freeze:** `ReleaseCandidate` + `release_candidates`; freezes version/SHA, migration/environment/rollback/evidence/checklist references.\n- **51 Launch/post-launch watch:** `LaunchWatchEvent` + `launch_watch_events`; `launch_allowed()` refuses unfrozen candidates or gates that are not VERIFIED/WAIVED with valid evidence.\n\n### Repository-level check visibility\n\n`.github/workflows/repository-gate.yml` now runs on every `main` push/PR and creates a single **Repository Gate** check. It waits for currently registered checks and becomes red when another check fails/cancels/times out, or green when the registered checks settle successfully. This makes the commit/repository status visible without opening Actions.\n\nThis gate is an aggregation/status surface, not a replacement for the underlying CI, worker, security, or external acceptance evidence.\n\n## Remaining phase queue — 52–60\n\n### Phase 52 — Series trailer planning\n- Trailer beat sheet, hook continuity, asset selection, duration constraints, and approval state.\n- Gate: representative series acceptance dataset.\n\n### Phase 53 — Burmese-first translation adapter\n- Translation provider interface, terminology glossary, fallback routing, subtitle-safe text normalization, and correction history.\n- Gate: representative Burmese/English acceptance corpus + provider terms.\n\n### Phase 54 — Sound / BGM workflow\n- Track metadata, loudness/ducking rules, rights metadata, cue timing, and export manifest integration.\n- Gate: licensed sample pack and human audio acceptance.\n\n### Phase 55 — Thumbnail candidate workflow\n- Deterministic candidate generation contract, 10→5 filtering, scoring, human selection, and persistence.\n- Gate: browser review E2E + representative visual dataset.\n\n### Phase 56 — LoRA / voice consistency seam\n- Model/profile versioning, character voice/style identity, consistency checks, fallback behavior, and commercial-use evidence fields.\n- Gate: live provider/model acceptance and human quality review.\n\n### Phase 57 — Social analytics import\n- Import adapters, source attribution, idempotent event ingestion, normalization, and analytics-to-experiment linkage.\n- Gate: real platform export/API sample validation.\n\n### Phase 58 — Archive / cold storage / PII purge\n- Archive state machine, legal-hold protection, retention execution, purge evidence, and restoreability checks.\n- Gate: real storage lifecycle + privacy/legal approval.\n\n### Phase 59 — Manual Mode production validation\n- 15–20 manual-video evidence bundle, production-time measurements, repeated-problem dataset, hook/subtitle coverage, commercial-use review, and MVP scope freeze.\n- Gate: owner/human acceptance.\n\n### Phase 60 — Final UI/state/component audit\n- Screen/state matrix, loading/error/empty states, responsive/WCAG checks, evidence capture, and release checklist reconciliation.\n- Gate: fresh browser/device evidence and manual sign-off.\n\n**Post-60 rule:** do not invent new phase numbers for live provider work. Live credential, runtime, legal, security, accessibility, and external acceptance items stay attached to the phase whose gate they verify.