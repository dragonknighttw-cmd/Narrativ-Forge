# Narrativ Forge — Roadmap

> Owner: Project maintainers  
> Update when: requirements, phase status, gates, or release criteria change  
> Last Updated: 2026-10-09  
> Do NOT put here: provider secrets, detailed runbook commands, or unsupported live-health claims

## Authority

This is the **only master execution roadmap**. Supporting documents contain implementation-specific detail. Code existence is not production evidence. The detailed item-by-item checklist lives in [`docs/MASTER_REMAINING_WORK.md`](docs/MASTER_REMAINING_WORK.md); keep phase authority and execution priority here.

## Completed Phases

| Phase | Scope | Status |
|---|---|---|
| 01 | Foundation & Security | DONE / VERIFY |
| 02 | Core Domain | DONE |
| 03 | Script Studio | DONE / VERIFY |
| 04 | Assets & Uploads | DONE / VERIFY |
| 05 | Processing Engine | FOUNDATION / VERIFY |
| 06 | Subtitle Studio | DONE / VERIFY |
| 07 | Review & Approval | DONE / VERIFY |
| 08 | Export & Publishing Preparation | DONE / VERIFY |
| 09 | Search & Analytics | DONE / VERIFY |
| 10 | Production Hardening | FOUNDATION / VERIFY |
| 11 | Business & Collaboration | FOUNDATION / VERIFY |
| 12 | Scale & Advanced | FOUNDATION / VERIFY |

## Active Phase

**Verification and evidence.** Main SHA `4dd3d4f0b761858c83047263a310dfa5429ab48b` includes merged PR #26 (SQLite restore integrity guard). Fresh main CI, Security, CodeQL, Repository Gate, backup/restore, worker and Windows/runtime evidence workflows are running; see [`docs/MASTER_REMAINING_WORK.md`](docs/MASTER_REMAINING_WORK.md) for run links and do not mark them passed until conclusions are recorded.

### Verified at the 2026-10-08 checkpoint

- Render API deployment is live from release SHA `1369d9a3e4d8896cf6024fa45fa6810cc3cee890`.
- Render health endpoint returns HTTP 200.
- Render readiness reports PostgreSQL=`ok` and Redis=`ok`.
- Cloudflare Whisper Worker `narrativ-forge-whisper` has a live 100% deployment and workers.dev reachability.

Evidence:
- https://narrativ-forge.onrender.com/api/v1/health
- https://narrativ-forge.onrender.com/api/v1/ready
- https://narrativ-forge-whisper.narrativ-forge.workers.dev
- https://github.com/dragonknighttw-cmd/Narrativ-Forge/commit/1369d9a3e4d8896cf6024fa45fa6810cc3cee890

### Still VERIFY

1. Real worker/media/storage completion.
2. Retry/DLQ/duplicate-dispatch/failover.
3. Real B2/Supabase/Cloudinary lifecycle.
4. Authenticated real Whisper + VTT + fallback E2E.
5. Google OAuth/Drive export/recovery.
6. SMTP.
7. Stripe.
8. Sentry.
9. Exact live Alembic migration head.
10. Backup/restore.
11. Production auth/tenant E2E.
12. Full browser E2E + load/performance.
13. Security/dependency/container scans on the release SHA.
14. Accessibility/responsive/WCAG review.
15. Legal/compliance.
16. External penetration testing.
17. Live provider limits/terms/commercial-use verification.

Priority order:
1. Freeze requirements and documentation ownership.
2. Complete the approved worker/media runtime path and authenticated Whisper E2E.
3. Verify storage and external integrations.
4. Run recovery, security, accessibility, E2E, and performance gates.
5. Complete UI screen/state/component audit.
6. Finish remaining Auto Production surfaces.
7. Final release audit.

## Future Phases / Workstreams

### Auto Production 13–17
- 13: Cross-platform export preparation.
- 14: Trend integration adapter.
- 15: A/B testing + feedback loop.
- 16: Series trailer planning.
- 17: Burmese-first translation adapter.

### Batches 18–36
18 publishing-preparation adapters/metadata/idempotency; 19 trend connectors; 20 experiment registry; 21 AI quality evaluation/provider ranking; 22 EDL/FCPXML/NLE manifests; 23 storage lifecycle/DR; 24 SRE/incident/compliance foundations; 25 character/style bible; 26 hook recommendation/episode scoring; 27 Burmese subtitle evaluation; 28 selective regeneration; 29 quota-aware scheduling; 30 human-review learning; 31 collaboration seam; 32 realtime notifications/presence; 33 usage quotas; 34 enterprise tenant policy; 35 demo/onboarding/support seam; 36 launch gate/pen-test remediation.

## Backlog / Requirements Completeness

The following must remain visible and are not considered lost during consolidation:

- Story ingestion → AI episode split → human approval.
- Eight hook families: Question, Shock, Mystery, Warning, Personal Story, Contrarian, Cliffhanger, Number.
- First 10 seconds: Hook → Pattern Interrupt → Context → Content.
- SEO/title/caption/hashtag/keyword/posting-time logic.
- Retention, emotional arc, cliffhanger/recap, engagement triggers.
- Thumbnail workflow: 10 candidates → 5 usable → human selection.
- Sound/BGM workflow.
- Subtitle styling.
- LoRA/voice consistency.
- Series Bible and continuity checks.
- Cross-platform preparation: TikTok/YouTube Shorts/Facebook Reels/Instagram Reels; preparation only, no direct publishing.
- Five-episode batch planning/calendar.
- Analytics feedback loop and evidence-based A/B learning.
- Video-generation adapter/fallback and watermark/commercial-use checks.
- Provider quota accounting and live-limit verification.
- Subtitle correction history/metrics/evaluation export.
- Social analytics import.
- Archive/cold-storage and PII purge.
- Backup/restore and rollback.
- Monitoring/incident/on-call.
- Full testing/security/accessibility/legal/pen-test release gates.

## Manual Mode validation gate

Before treating Manual Mode as production-ready, collect human evidence including 15–20 manual videos, production logs, multiple hook types, subtitle styles, production-time measurements, commercial-use review, repeated-problem dataset, and MVP scope freeze.

## Release gate

Production Ready requires fresh evidence for:
- real worker + representative media;
- queue → worker → FFmpeg/Whisper → DB/storage;
- retry/DLQ/failover;
- real OAuth/Drive export/recovery;
- SMTP;
- Stripe;
- Sentry;
- backup/restore;
- live provider limits/terms;
- production auth/tenant E2E;
- full E2E;
- load/performance;
- security scan;
- accessibility/responsive;
- legal/compliance;
- external penetration testing.

## Deferred

- Direct social publishing.
- Full mobile client.
- Paid always-on worker unless needed.
- Production LoRA/video-generation pipeline until provider/legal/runtime evidence exists.

## Blocked

Anything requiring user/provider credentials, a real worker machine, real media, provider consoles, or external legal/security sign-off remains VERIFY/PENDING until evidence exists.

## Evidence rule

Never promote code-configured to VERIFIED from credentials alone. Never promote a live integration from unit tests alone.

## Release gate close-out checkpoint — 2026-10-08

### Worker

**BLOCKED — owner provisioning required.**

Worker code is complete and deployable:
`web-platform/backend/Dockerfile.worker` → Celery → Redis → PostgreSQL → FFmpeg/Whisper.

The connected Render service is a Free web service. Render documents background workers as a separate service type whose compute plans are paid; Free instances are available for web services, Postgres and Key Value. citeturn0search0turn0search1

Prepared blueprint: `render.worker.yaml`.

### Gate status

| Gate | Status |
|---|---|
| 1 Real media E2E | BLOCKED — worker |
| 2 Retry/DLQ/failover | BLOCKED — worker |
| 3 Storage lifecycle | PENDING |
| 4 Whisper/fallback E2E | BLOCKED — worker |
| 5 Google Drive OAuth/export/recovery | PENDING |
| 6 SMTP | PENDING |
| 7 Stripe | PENDING |
| 8 Sentry | PENDING |
| 9 Exact live Alembic head | VERIFY — external DB inaccessible |
| 10 Backup/restore | PENDING |
| 11 Auth/cross-tenant E2E | PENDING |
| 12 Full E2E/load/performance | BLOCKED — worker dependency |
| 13 Security scans | EXTERNAL ACTION |
| 14 Accessibility/WCAG | EXTERNAL ACTION |
| 15 Legal/compliance | EXTERNAL ACTION |
| 16 Pen-test | EXTERNAL ACTION |
| 17 Provider terms/limits/commercial use | EXTERNAL ACTION |

No gate is promoted to VERIFIED by source-code or configuration evidence alone.
\n\n## Consolidated continuation roadmap — Phases 15–60\n\nThe canonical roadmap now incorporates the execution/evidence queue used by `PHASE_EXECUTION.md`. These phases are implementation continuations, not claims that the corresponding live gates are verified.\n\n### Phases 15–36\n15 cross-platform export preparation; 16 trend adapter; 17 A/B testing + feedback; 18 publishing metadata/idempotency; 19 trend connectors; 20 experiment registry; 21 AI quality/provider ranking; 22 EDL/FCPXML/NLE manifests; 23 storage lifecycle/DR; 24 SRE/incident/compliance; 25 character/style bible; 26 hook recommendation/episode scoring; 27 Burmese subtitle evaluation; 28 selective regeneration; 29 quota-aware scheduling; 30 human-review learning; 31 collaboration; 32 realtime/presence; 33 usage quotas; 34 enterprise tenant policy; 35 demo/onboarding/support; 36 launch gate/pen-test remediation.\n\n### Phases 37–45\n37 release train/migration safety; 38 cost governance; 39 data lifecycle/privacy; 40 DR automation; 41 multi-region readiness; 42 advanced queue scheduling; 43 evaluation dataset governance; 44 model/provider change management; 45 final operating maturity.\n\n### Phases 46–51 — implemented foundations\n46 evidence ledger; 47 provider acceptance matrix; 48 production E2E rehearsal seam; 49 billing/entitlement reconciliation; 50 release-candidate freeze; 51 final launch/post-launch watch.\n\nImplementation evidence now exists in `web-platform/backend/app/services/release_maturity.py`, `app/models/core.py`, migration `0017_release_maturity`, unit tests, and `.github/workflows/repository-gate.yml`.\n\n**Important:** these are repository implementation foundations. They do not promote live worker/provider/billing/legal/security/manual gates to VERIFIED.\n\n### Phases 52–60 — pre-staged remaining backlog\n52 series trailer planning; 53 Burmese-first translation adapter; 54 sound/BGM workflow; 55 thumbnail candidate workflow; 56 LoRA/voice consistency seam; 57 social analytics import; 58 archive/cold-storage/PII purge; 59 Manual Mode production validation; 60 final UI/state/component audit.\n\nThe original requirements backlog remains covered: eight hook families, first-10-second structure, SEO metadata, retention/emotional arc, thumbnail 10→5 review, sound/BGM, subtitle styling, LoRA/voice consistency, Series Bible, five-episode planning, analytics/A-B feedback, video-generation fallback/watermark/commercial-use checks, quota accounting, subtitle correction metrics, social analytics import, archive/PII purge, backup/restore, monitoring/incident/on-call, and full testing/security/accessibility/legal/pen-test gates.\n\n### Execution rule\n\nCode-only foundations continue on `main` in parallel where independent. Live credentials, paid worker capacity, provider terms/limits, billing, legal/privacy approval, penetration testing, accessibility/manual acceptance, and real-media/browser evidence remain explicit gates. No secret is stored in the repository.

### Phases 61–68 — pre-staged continuation
61 performance/cost optimization; 62 worker-fleet autoscaling; 63 content provenance/lineage; 64 advanced collaboration/enterprise audit; 65 provider adapter/marketplace seam; 66 localization quality operations; 67 monetization expansion; 68 post-launch SLO/error-budget operations.

Implementation for 52–60 is now present in `phase_52_60.py` with unit coverage. Phases 61–68 are backlog contracts to be implemented next; their live acceptance gates remain explicit and cannot be inferred from code-only tests.


## Phase 61–68 code-foundation progress — 2026-10-08

Code-only foundations are now staged in `web-platform/backend/app/services/phase_61_68.py` with unit coverage in `tests/test_phase_61_68.py`: performance/cost budgets, worker autoscaling policy, provenance lineage, enterprise permissions, provider capability discovery, localization quality thresholds, billing metering validation, SLO budgets and incident/rollback policy. Live telemetry, billing, provider, enterprise and post-launch acceptance remain external gates.


## Phase 69–76 code-foundation progress — 2026-10-08

Code-only foundations are staged in `web-platform/backend/app/services/phase_69_76.py` with unit coverage in `tests/test_phase_69_76.py`: rollout/cohort policy, schema-drift detection, restore verification, privacy-request closure, secret/config readiness, dependency-license allowlisting, chaos-drill acceptance, and deterministic release evidence packs. These contracts do not claim live backup, privacy/legal, secret-manager, license, chaos or release acceptance.

### Phase 69–76 queue
69 progressive rollout/cohort control; 70 schema/data-quality drift; 71 restore verification; 72 privacy/data-subject operations; 73 secret/config readiness; 74 dependency/license governance; 75 chaos/recovery drills; 76 final release evidence pack.


### Phases 77–84 — pre-staged next queue
77 capacity/tenant quota forecasting; 78 API versioning/deprecation contracts; 79 migration retirement and data cleanup; 80 portable tenant export/import; 81 incident communications and status-page evidence; 82 support SLA/escalation operations; 83 provider marketplace billing/settlement seam; 84 final governance/ownership matrix and release evidence reconciliation.

Implementation rule: these remain code/evidence work after 69–76 are exhausted. Any live provider, billing, legal, privacy, security, accessibility, human acceptance or production-runtime dependency remains an explicit external gate and is never inferred from unit tests.


## Phases 77–84 — code-only foundations complete

77 capacity/quota forecasting; 78 API versioning/deprecation; 79 migration retirement/data cleanup; 80 portable tenant export/import; 81 incident communications/status evidence; 82 support SLA/escalation; 83 provider settlement seam; 84 governance/ownership/evidence reconciliation.

Implementation is present in `phase_77_84.py` with unit coverage in `test_phase_77_84.py`. Live operational, provider, billing, privacy/legal, security and human acceptance gates remain separate and are not inferred from these tests.
