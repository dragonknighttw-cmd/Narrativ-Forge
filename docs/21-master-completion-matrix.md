# Narrativ Forge — Master Completion & Reconciliation Matrix

Last reconciled: 2026-10-07

## Authority

This matrix reconciles:
1. `roadmap.md` in the repository.
2. Final Master Plan / Comprehensive Remediation Plan source material.
3. `docs/04-current-vs-target.md`.
4. `docs/05-execution-roadmap.md`.
5. `docs/09-auto-production-expansion.md`.
6. The 12 formal phases and Expanded Auto Production workstreams 13–17.
7. Batches 18–36 and the live-verification gates.

### Status meanings

- **CODE-DONE** — repository implementation is present for the scoped contract/path.
- **FOUNDATION** — deterministic/code contract exists, but end-to-end workflow or production wiring is incomplete.
- **VERIFY** — code exists but real provider/runtime/account evidence is required.
- **USER/LIVE** — requires a real machine, credential, provider console, mailbox, account, or production environment.
- **TODO** — target behavior is not sufficiently implemented yet.
- **RESERVE** — intentionally deferred by product boundary or future scope.

Code existence never upgrades a live integration to DONE.

## Product boundary

Narrativ Forge remains a private, invite-only Burmese short-form video production system with Manual + Auto Mode and mandatory human approval.

Core workflow:
Idea → Structure → Script → Assets → Processing → Subtitle → Review → Output

Google Drive is an approved-output destination, not the workflow database.

Strict exclusions:
- Logixa Flow
- Aether Bridge
- public registration
- public profiles
- public browsing/comments
- direct TikTok/YouTube/Facebook/Instagram publishing
- external downstream delivery
- secrets in source/docs

## Formal phases

| Phase | Scope | Current status |
|---|---|---|
| 01 | Foundation & Security | CODE-DONE / VERIFY |
| 02 | Core Domain | CODE-DONE |
| 03 | Script Studio | CODE-DONE / VERIFY |
| 04 | Assets & Uploads | CODE-DONE / VERIFY |
| 05 | Processing Engine | FOUNDATION / LIVE VERIFY |
| 06 | Subtitle Studio | CODE-DONE / VERIFY |
| 07 | Review & Approval | CODE-DONE / VERIFY |
| 08 | Export & Publishing Preparation | CODE-DONE / VERIFY |
| 09 | Search & Analytics | CODE-DONE / VERIFY |
| 10 | Production Hardening | FOUNDATION / VERIFY |
| 11 | Business & Collaboration | FOUNDATION / VERIFY |
| 12 | Scale & Advanced | FOUNDATION / VERIFY |

## Expanded Auto Production 13–17

| Workstream | Scope | Current status |
|---|---|---|
| 13 | Cross-platform export preparation | FOUNDATION |
| 14 | Trend integration adapter | FOUNDATION |
| 15 | A/B testing + feedback loop | FOUNDATION |
| 16 | Series trailer planning | FOUNDATION |
| 17 | Burmese-first translation adapter | FOUNDATION |

## Batch 18–24

| Batch | Scope | Current status |
|---|---|---|
| 18 | Multi-platform publishing preparation adapters, metadata validation, idempotency | FOUNDATION; no direct publishing |
| 19 | Trend connectors, TTL/cache, attribution, graceful fallback | FOUNDATION |
| 20 | Experiment registry/allocation/outcomes/winner guardrails | FOUNDATION |
| 21 | AI quality evaluation, provider ranking, regression-test contracts | FOUNDATION |
| 22 | EDL/FCPXML/NLE manifest and timeline validation | FOUNDATION |
| 23 | Storage lifecycle, retention safety, DR target contracts | FOUNDATION |
| 24 | SRE alerts, incident/compliance gate foundations | FOUNDATION |

## Batch 25–36

| Batch | Scope | Current status |
|---|---|---|
| 25 | Character/style bible | FOUNDATION |
| 26 | Hook recommendation + episode scoring | FOUNDATION |
| 27 | Burmese subtitle quality / Zawgyi-Unicode evaluation | FOUNDATION |
| 28 | Dependency-aware selective regeneration | FOUNDATION |
| 29 | Quota-aware batch scheduling | FOUNDATION |
| 30 | Human review learning | FOUNDATION |
| 31 | Collaboration presence / Yjs seam | FOUNDATION |
| 32 | Realtime notifications/presence seam | FOUNDATION |
| 33 | Usage quota enforcement | FOUNDATION |
| 34 | Enterprise tenant policy | FOUNDATION |
| 35 | Demo/onboarding seed + support seam | FOUNDATION |
| 36 | Launch gate + external pen-test remediation seam | FOUNDATION |

## Core product capabilities

### Auth / access
- Invite-only access: CODE-DONE / VERIFY
- Secure session configuration: CODE-DONE / VERIFY
- RBAC and permission checks: CODE-DONE / VERIFY
- Session-expired / permission-denied UI states: FOUNDATION
- Fine-grained tenant/resource permissions: FOUNDATION / VERIFY

### Ideas / series / episodes
- Ideas CRUD: CODE-DONE
- Series / seasons / episodes: CODE-DONE
- Episode ordering/uniqueness: CODE-DONE
- Episode workflow control center: CODE-DONE / VERIFY
- Continuity metadata: FOUNDATION

### Script / scene
- Script CRUD/versioning/autosave: CODE-DONE / VERIFY
- Immutable historical versions: FOUNDATION
- Optimistic locking / 409 conflict: CODE-DONE / VERIFY
- Scene breakdown/reorder/mapping: CODE-DONE / VERIFY
- AI suggestions/hook insertion: FOUNDATION
- Content extensions: FOUNDATION / VERIFY

### Assets / uploads
- Asset metadata/versioning/checksum/dedupe: CODE-DONE / VERIFY
- Original preservation / soft-delete: CODE-DONE
- MIME/extension/filename/path safety: CODE-DONE
- Resumable upload session/chunk/offset/checksum contract: FOUNDATION
- Real flaky-network upload E2E: USER/LIVE
- Storage routing B2/Supabase/Cloudinary: CODE-DONE / VERIFY

### Processing
- Celery/Redis job architecture: CODE-DONE / VERIFY
- Worker dispatch/locking/retry/DLQ foundations: CODE-DONE / VERIFY
- FFmpeg pipeline: FOUNDATION / LIVE VERIFY
- Whisper pipeline: FOUNDATION / LIVE VERIFY
- Timeout/process-group/orphan protection: FOUNDATION / VERIFY
- Real media worker smoke test: USER/LIVE
- 15–30 min MVP benchmark / 7–15 optimized target: USER/LIVE

### Subtitle
- Transcript/cue/SRT/VTT: CODE-DONE / VERIFY
- Burmese editor/timing gates: CODE-DONE
- Reading-time/overlap/missing-cue validation: CODE-DONE
- Zawgyi/Unicode handling: FOUNDATION
- >95% Zawgyi detection target: VERIFY with evaluation corpus
- Correction history/metrics/training export: FOUNDATION

### Review / approval
- Review checklist: CODE-DONE
- Critical issue blocking: CODE-DONE
- Approval audit: CODE-DONE
- Approved-only export: CODE-DONE
- Real browser/E2E approval path: USER/LIVE

### Export / publishing preparation
- Drive package/manifest/checksum/idempotency: CODE-DONE / VERIFY
- Direct social publishing: RESERVE / OUT OF SCOPE
- Platform-specific metadata/format preparation: FOUNDATION
- Manual publishing record: FOUNDATION / VERIFY
- Social analytics import/manual entry: FOUNDATION / VERIFY

## Auto Production expansion targets

- Story upload + AI episode split: FOUNDATION
- 8 hook families + candidate ranking: FOUNDATION
- SEO metadata: FOUNDATION
- Retention/pacing/emotional arc: FOUNDATION
- Thumbnail candidate selection: FOUNDATION
- Sound/BGM plan: FOUNDATION
- Character/voice consistency: FOUNDATION
- Series Bible + continuity: FOUNDATION
- Trend ingestion: FOUNDATION
- Cross-platform preparation: FOUNDATION
- Batch generation/calendar: FOUNDATION
- Burmese-first translation: FOUNDATION
- Feedback/A-B experimentation: FOUNDATION
- Video generation adapter + fallback contract: FOUNDATION
- Watermark/commercial-use policy: FOUNDATION
- Real provider execution/commercial terms: USER/LIVE / VERIFY

## UI / design system

The repository roadmap retains the original 26-screen baseline plus the expanded Auto Production screen targets. The final screen count must be re-baselined after deciding which items are screens vs tabs/panels.

Coding foundation:
- semantic tokens: FOUNDATION/CODE-DONE
- accessible reusable primitives: FOUNDATION/CODE-DONE
- focus/reduced-motion/touch-target rules: FOUNDATION
- 33-component target: FOUNDATION
- full screen-level state audit: TODO/VERIFY
- responsive desktop/tablet/mobile audit: TODO/VERIFY
- WCAG AA audit: TODO/VERIFY
- Burmese typography/readability audit: TODO/VERIFY

Required state coverage:
empty, loading, uploading, processing, completed, failed, retrying, rejected, offline/read-only, permission denied, session expired, Drive disconnected, Drive export failed, storage warning, unsupported file, critical quality issue.

## Business / collaboration

- Organization/membership/invitation: CODE-DONE / VERIFY
- Magic link: CODE-DONE / VERIFY
- Usage metering: FOUNDATION / VERIFY
- Stripe checkout/portal/webhook foundation: FOUNDATION / LIVE
- Subscription/quota enforcement: FOUNDATION
- Yjs collaboration: FOUNDATION seam / LIVE integration TODO
- Realtime notifications/presence: FOUNDATION
- Demo tenant / sample seed: FOUNDATION
- Support/ticket workflow: FOUNDATION
- Transactional email delivery: USER/LIVE

## Storage / DR / SRE

- Reference-safe lifecycle policy: CODE-DONE
- 80/90/95% threshold contract: CODE-DONE
- Retention cleanup implementation: FOUNDATION
- Archive/cold-storage execution: TODO/VERIFY
- Restore drill: USER/LIVE
- RPO/RTO evidence: USER/LIVE
- Structured logging/observability: FOUNDATION / VERIFY
- Sentry production event/alert: USER/LIVE
- Alert thresholds/incident contracts: FOUNDATION
- Status/on-call/incident communication: TODO/VERIFY

## Security / legal

- Secret hygiene / runtime validation: CODE-DONE / VERIFY
- Tenant scoping in critical routes: CODE-DONE / VERIFY
- Rate limits: FOUNDATION / VERIFY
- Dependency/SAST/container scan configuration: FOUNDATION / VERIFY
- Cross-tenant E2E: USER/LIVE
- Backup/restore: USER/LIVE
- Deletion/PII purge pipeline: FOUNDATION / VERIFY
- Retention policy: FOUNDATION
- Terms / Privacy / DPA / DMCA: TODO
- External penetration test: USER/LIVE
- Final security evidence: USER/LIVE

## CI / testing

- Unit test foundation: CODE-DONE
- Integration suite: FOUNDATION / VERIFY
- Full E2E workflow: TODO/VERIFY
- Load/k6: TODO/VERIFY
- CodeQL/Bandit/pip-audit/npm audit/Trivy: FOUNDATION / VERIFY on release SHA
- Fresh CI/security evidence for latest code-changing SHA: VERIFY
- Frontend Vitest coverage: VERIFY/TODO
- Accessibility automated + manual audit: TODO/VERIFY

## Production deployment

- Frontend/backend hosting: FOUNDATION / VERIFY
- Managed PostgreSQL: VERIFY
- Managed Redis: VERIFY
- Worker runtime: USER/LIVE
- Storage: VERIFY
- Google OAuth: USER/LIVE
- SMTP: USER/LIVE
- Stripe: USER/LIVE
- Sentry: USER/LIVE
- DNS/HTTPS/CORS/env/secrets: USER/LIVE
- Backup/restore: USER/LIVE
- Rollback/smoke/full-content tests: USER/LIVE

## Manual Mode exit gate

- 15–20 manual videos
- production log
- 3+ hook types
- 2+ subtitle styles
- production-time measurements
- commercial-use review
- repeated-problem dataset
- MVP scope freeze

These are human evidence gates and cannot be synthesized by code.

## Final release gate

A production-ready claim requires all applicable rows to be either:
1. CODE-DONE with automated evidence,
2. VERIFY with fresh live evidence,
3. RESERVE by explicit product decision.

The following are hard blockers until real evidence exists:
- real worker + representative media
- Queue → Worker → FFmpeg/Whisper → DB/storage
- retry/DLQ/failover
- real OAuth/Drive export/re-export/recovery
- real SMTP invitation/magic link
- Stripe lifecycle/webhooks
- Sentry event/alert
- backup/restore drill
- live provider limits/terms
- production auth/tenant E2E
- full integration/E2E suite
- load/performance benchmark
- security scan on release SHA
- accessibility/responsive audit
- legal/compliance documents
- external penetration test

## Next execution order

1. Finish remaining code-only TODOs and foundation wiring.
2. Finish 33-component/screen-level UI audit.
3. Finish versioning/content-extension/selective-regeneration integration paths.
4. Finish storage cleanup/monitoring implementation.
5. Finish auth/magic-link/error-path test coverage.
6. Finish expanded Auto Production schema/API/worker/UI wiring where practical.
7. Reconcile docs/README/roadmap after each meaningful batch.
8. Then execute the consolidated live gate in one verification window:
   worker → real media → storage → Whisper → subtitles → review → approval → Drive → SMTP → Stripe → Sentry → backup/restore → E2E → load/security/a11y → final audit.
