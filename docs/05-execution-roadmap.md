# Execution Roadmap

## P0 — Verification first
1. Real B2 upload/download/delete.
2. Real Supabase Storage lifecycle.
3. Real Cloudinary upload.
4. Hybrid-storage E2E.
5. Cloudflare Whisper: real audio → VTT → Subtitle Studio.
6. Verify Whisper quota guard → Celery fallback.
7. Real Celery worker/runtime smoke test.
8. Retry/DLQ/duplicate-dispatch verification.
9. Google OAuth callback + real Drive export.
10. Idempotent re-export + partial-upload recovery.
11. Stripe webhook lifecycle.
12. SMTP invitation/magic-link delivery.
13. Sentry production event.
14. Full auth E2E.
15. Cross-tenant isolation E2E.
16. Backup/restore drill.

## P1 — Product completion
- Complete UI states.
- Responsive mobile/tablet audit.
- WCAG accessibility audit.
- Final UI polish.
- Verify explicit versioning / selective regeneration / content-extension / character requirements that are actually needed.
- Verify all quality gates and workflow transitions.
- Verify production log + analytics feedback loop.

## Feedback loop

```
Manual Data → Hook Library → Auto Defaults → Human Approve
```

### Rule
Do not optimize from one video's views alone.

Wait until at least **5–10 content pieces** exist, then compare:
- Hook performance.
- Retention/engagement signals.
- Production effort/time.
- Subtitle style results.
- Other available content-quality signals.

The purpose is to turn manual production data into better defaults while keeping human approval in the loop.

## P1 — Security / operations
- Final dependency/security scan.
- Artifact/container scan where applicable.
- Pen-test/security review.
- Backup retention + restore drill.
- Incident/runbook drill.
- Monitoring/alert verification.

## P1 — Business / legal
- Terms of Service.
- Privacy Policy.
- DPA/data handling where required.
- Stripe production verification.
- Final business/legal review.

DMCA/reporting and local payment integration are not automatic blockers unless product scope changes.

## Release gate
Production-ready only after real storage, transcription, worker, Drive export/idempotency, auth/tenant E2E, backup/restore, monitoring, security, accessibility, UX, and required business/legal checks pass.

Until then: **Implementation-complete / Verification-pending**.


## P0.5 — CI / repository health
Before feature expansion, keep the repository green:
1. Cancel stale/in-progress historical GitHub Actions runs.
2. Confirm concurrency cancellation keeps only the newest run per workflow/ref.
3. Confirm docs-only changes do not trigger CI/CodeQL/Security.
4. Run the latest CI, CodeQL, and Security workflows on the repaired main commit.
5. Fix failures from newest runs only; do not chase obsolete cancelled runs.

## P1 — Expanded Auto Production
After foundation verification, implement in this order:
1. Story ingestion + AI episode split review.
2. Series Bible + character/voice profile foundations.
3. Hook Library + hook generation + performance fields.
4. Script/retention/emotional-arc/pacing quality analysis.
5. SEO metadata + engagement triggers.
6. Thumbnail pipeline + visual variety.
7. Sound design + music matching.
8. Video generation adapter + provider fallback + quota tracking.
9. Watermark/commercial-use quality gates.
10. Selective regeneration integrated with episode/scene versions.
11. Batch generation + daily-limit-aware queue.
12. Series calendar + publishing preparation.
13. Cross-platform export variants.
14. Trend integration adapter.
15. A/B testing + feedback loop.
16. Series trailer.
17. Translation only after Burmese-first workflow is stable.

## Scope rule for the expanded plan
Do not build all new tables/screens blindly. For each capability: schema → API/service → worker job if needed → UI → tests → real integration check → audit/approval behavior. A feature is DONE only after its end-to-end path works.

## Revised release order
Repository Green → Real Infrastructure Verification → Core Workflow E2E → Expanded Auto Production → UX/A11y/Security Hardening → Business/Legal → Release Gate.


## Explicit capacity / performance / UI completion checklist

Before calling the expanded product production-ready, also close these five tracked items:

1. **Agnes daily-limit calculation:** use the current MVP planning baseline of **500 sec/day ÷ ~25 sec/video = 20 videos/day**, then verify the real provider quota and enforce it in the generation queue.
2. **Processing target:** benchmark the real worker path and meet the MVP target of **15–30 minutes/video** under representative processing conditions.
3. **Groq daily limit:** use **1,000 requests/day** as the conservative planning baseline, verify the live account/model limit, and implement request-budget tracking plus fallback behavior.
4. **Design System:** implement Colors, Typography, Spacing, semantic states, responsive rules, and accessibility tokens in the actual UI, then audit them.
5. **Component Library:** implement and audit the **33-component target** from docs/07-ui-design.md, including required variants and loading/empty/error/success/disabled/permission/responsive/accessibility states.

These five items are explicit roadmap requirements and must remain visible in the remaining-work list until verified.


## P0 — Worker runtime strategy (free-first)

The production worker host is intentionally separated from the Render Web Service.

### Current plan

1. **Now:** use one or two Windows PCs as Celery worker hosts.
2. Both PCs run the repository's existing `web-platform/backend` worker code; do not fork a separate worker application.
3. Home PC may host the single Celery Beat instance; Office PC is a worker only by default.
4. Upstash Redis remains the shared broker/queue.
5. FFmpeg runs locally; Cloudflare Whisper remains the default transcription path.
6. Verify queue → worker → FFmpeg → DB/storage → retry/DLQ → failover before marking the worker runtime DONE.

### Paid migration reserve

When local processing becomes the bottleneck, the same worker contract may move to:
- Render Background Worker (paid), or
- a paid VPS / other verified always-on host.

This is a host migration, not an application rewrite. No paid worker should be provisioned while the project remains free-only without explicit approval.

### Storage lifecycle gate

Before production-ready status:
- usage monitoring exists for local/B2/Supabase/Cloudinary/Drive,
- 80/90/95% thresholds are defined,
- retention cleanup is reference-safe,
- raw/intermediate cleanup never deletes the only approved final output,
- cleanup and emergency procedures are tested.

Detailed operational plan: `docs/10-runtime-and-storage-lifecycle-plan.md`.


## Phase work while Local Worker gate is paused

The Local Worker runtime gate is intentionally deferred until the user's Home/Office machine test window. It must not block implementation work that can be completed and tested without a live worker.

Current coding-first progress:
1. Hook library now accepts all 8 documented hook families, including **Number**.
2. Evidence-backed hook recommendations are available after the required **5 published samples**, using completion, views, and shares rather than one-video optimization.
3. Provider quota budgeting primitives are implemented for the current planning baselines: **Agnes 500 sec/day** and **Groq 1,000 requests/day**, with idempotent reservation plus warning/fallback thresholds.
4. These provider budgets remain VERIFY until live account/model limits and actual provider adapters are connected.

The deferred Local Worker gate remains separate:
**Local Worker → real FFmpeg → Queue → DB → Storage → Retry/DLQ → Failover**.


## Coding-First Progress — Phases 7–9

While live-worker and credential-gated verification remains paused, the implementation track continues:
- Phase 7: semantic design tokens, accessible reusable UI primitives, focus states, 44px touch targets, reduced-motion handling.
- Phase 8: release hardening checklist remains required for production; tenant isolation, idempotency, retry/DLQ, observability, backup/restore and performance are verification gates, not code-only DONE claims.
- Phase 9: release candidate checklist is defined around green CI/security, production infrastructure verification, rollback readiness, human approval/export safety, and unresolved external gates.

No Phase 8/9 production-ready claim is made until live verification gates pass.


## Ownership split — 2026-10-07

### USER: live / credential / machine work

| Item | Why user action is required | Done condition |
|---|---|---|
| Local Home/Office worker | Requires an always-on local Windows machine with FFmpeg and repo dependencies | Real Celery worker consumes a real job |
| Queue → FFmpeg → DB/storage E2E | Must execute against the real local worker | Real output + DB state + artifact lifecycle verified |
| Retry/DLQ + failover | Requires killing/failing a real worker during processing | Retry and failover observed without data loss |
| Production auth + tenant E2E | Needs the real production environment/session/browser context | Login, session and tenant isolation pass |
| Google OAuth/Drive | Needs OAuth client/consent and callback credentials | Export + re-export + partial recovery pass |
| SMTP delivery | Needs a real SMTP provider/mailbox | Invitation + magic-link email received and consumed |
| Stripe lifecycle | Needs Stripe account/webhook configuration | API + webhook + retry/idempotency pass |
| Sentry event/alerts | Needs DSN and alert configuration | Real event received and alert path verified |
| Backup/restore drill | Depends on provider permissions/tooling | Backup restored into a safe target and validated |
| Agnes/Groq live limits | Depends on provider account/model quotas | Live limits recorded and enforced |
| 15–30 min/video benchmark | Requires real worker + representative media | Benchmark meets target or has documented capacity decision |

### ASSISTANT: coding / test / documentation work

The assistant should continue these without waiting for the user gates:

1. Harden and test provider quota guards, adapter fallback, and failure semantics.
2. Finish selective regeneration/versioning and content-extension test coverage.
3. Finish storage lifecycle cleanup, monitoring, safety checks, and tests.
4. Complete magic-link/auth tests and production-safe failure handling.
5. Expand tenant-isolation, idempotency, retry/DLQ, security, and observability test coverage.
6. Continue the 33-component design-system/UI audit with responsive, loading, empty, error, success, disabled, permission, focus, and accessibility states.
7. Continue Auto Production foundations in schema → API/service → worker → UI → tests order.
8. Keep docs 04/05/10/11 synchronized after each meaningful implementation batch.
9. Re-run CI/security on each code-changing release candidate and fix failures before calling the code batch complete.

### Current verified infrastructure baseline

- **B2:** real upload/download/checksum/delete round-trip passed.
- **Supabase Storage:** real upload/download/delete round-trip passed.
- **Cloudinary:** real upload/download/delete round-trip passed.
- **Cloudflare Whisper:** real audio → Whisper → VTT path passed.
- **Redis:** real temporary SET → GET → DEL passed.
- **Production backend/Postgres:** live deployment and migration path verified.

These prove infrastructure components individually; they do **not** replace the still-pending end-to-end worker runtime/failover gate.


## Coding-track progress — 2026-10-07 (continued)

The paused Local Worker gate is not blocking the coding track. The current implementation pass added:
1. Production-sized Auto Mode plan normalization.
2. Selective regeneration normalization and tenant scope enforcement.
3. SEO/thumbnail/sound/platform-export planning primitives.
4. Batch/calendar and A/B testing foundations.
5. Eight-family hook engineering foundation.
6. Provider fallback and retryable-error primitives.
7. Storage threshold and cleanup-safety primitives.
8. Magic-link and production-foundation test coverage.
9. UI design-token alignment fixes.

Live worker, external provider, OAuth/Drive, SMTP, Stripe, Sentry, backup/restore, and benchmark gates remain assigned to live verification.
