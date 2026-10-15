# Authoritative roadmap checkpoint — 2026-10-15 UTC

- **Latest application-code commit observed:** `d370921054b92bbc89b5cf647680543f714c906d`.
- **Immediate blockers:** hosted Render API/frontend are on older commit `3b1b3766f2fb132bf4d80203e7174562f2879d9a` and auto-deploy is disabled; canonical frontend and database/project mapping need confirmation; Supabase security advisor findings need triage; real worker/media E2E and Burmese ASR human-quality acceptance remain open.
- **Full prioritized audit checklist:** [INFRASTRUCTURE_AUDIT.md](INFRASTRUCTURE_AUDIT.md).
- **Release remains PENDING — NOT PRODUCTION READY.** Do not redeploy, change RLS, drop indexes, or provision paid resources without the appropriate evidence and owner approval.

The checkpoints below are historical. Use this block as the current priority summary.

---

# Authoritative roadmap checkpoint — 2026-10-14 UTC

- **Base main SHA for this checkpoint:** `4959810fc1a7449cc714084ca0169557dce02513`.
- **Recently completed:** PR #80 build-artifact hygiene; PR #83 Series Bible persistence; PR #84 continuity tests; PR #85 subtitle API tenant/role/immutability tests; PR #86 Script Studio/scene API acceptance; PR #88 Series Bible UI reload persistence; PR #89 upload/source checksum, processed-output integrity, mock processing completion, and subtitle SRT export E2E.
- **Verified:** PRs #85 and #86 passed exact-head backend/integration, frontend, E2E, CodeQL/security, runtime/package, and Real Worker Evidence. PRs #88 and #89 passed their applicable backend/integration, frontend E2E, CodeQL/security, runtime/package, and repository checks. PR #89 reported backend **309 passed, 3 skipped**, integration **75 passed, 1 skipped**, E2E **4 passed**.
- **Remaining priorities:** (1) authenticated non-mock media/provider E2E and processing error/retry paths; (2) asset validation and tenant/role acceptance for edge cases; (3) human Burmese ASR quality review against a dialect-specific reference transcript (still unaccepted and explicitly deferred); (4) managed restore/provider integration and external accessibility, privacy/legal/commercial-use, and independent security sign-offs.
- **Release remains PENDING — NOT PRODUCTION READY.** No production deployment, paid resources, production-data mutation, or cloud inference performed.

The older roadmap checkpoints below are historical.


---

# Current roadmap checkpoint — 2026-10-14 UTC

- **Base main SHA for this checkpoint:** `d6709d8b84d66f019015db9d6a9010ce9e923ccb` (PR #81 refreshes status after PRs #79 and #80).
- **Latest application-code SHA:** `6dbd4fabe715c06b565c6e53cf187b7373bbb9df`; approval response bug fixed and merged in [PR #77](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/77). Exact-SHA CI, Security, CodeQL, Repository Gate, runtime/package evidence and Real Worker Evidence passed on the tested candidate SHA.
- The overnight platform features are treated as **implemented foundations needing acceptance**, not work to reimplement. Priority is feature persistence/authorization acceptance, Burmese ASR quality review, authenticated local/staging E2E, and external release gates. The generated TypeScript build cache was removed and `*.tsbuildinfo` ignored in merged PR #80.
- Burmese ASR is **not accepted**: three local Whisper configurations on the reported older SHA produced no Myanmar-script characters and were rejected by the language guard. Do not spend cloud inference quota without explicit approval.
- **Release remains PENDING — NOT PRODUCTION READY.** No production deployment or paid worker provisioning is implied by passing CI.

---

## Latest plan reconciliation — 2026-10-14 UTC

- **Latest main SHA:** `fe17d74229cb51ca4eec125b720594fb85ebbbb6`.
- **Latest application-code SHA:** `f2f45cfca45f6e36408a8674d3d96eaec61c8fd2`; current main is 17 commits ahead of deployed baseline `3b1b3766f2fb132bf4d80203e7174562f2879d9a` (0 behind). Recent feature commits add the Script Studio/scene planning, batch generation, thumbnail/subtitle, 9:16, asset/processing, Series Bible, Burmese typography and mock RAG foundations.
- **Planning change, not code change:** treat these new features as implemented foundations that now require exact-SHA CI and acceptance verification. Do not reset the roadmap or reimplement them from scratch.
- **ASR decision:** local test results on SHA `3b1b3766` failed Burmese speech quality across three Whisper configurations; script guard rejection worked. No live Cloudflare inference was used. Burmese quality remains a release blocker until human dialect/reference-transcript review and a successful reviewed output.
- **Immediate priority:** fix the confirmed `review.py` `approve_review()` undefined `approved_at` defect in a separate code change; verify exact-SHA CI/Security/CodeQL/Repository Gate; acceptance-test new feature workflows and tenant/role guards; rerun ASR guard tests; resolve generated `tsconfig.tsbuildinfo` tracking.
- **Release status:** **PENDING — NOT PRODUCTION READY**. No deployment, paid worker provisioning, quota-consuming inference, or production-data mutation is authorized by this plan update.

## Post-merge execution checkpoint — 2026-10-13 UTC

- PRs #72 and #73 are merged. The application-code checkpoint is `dfff46a5335833723e403b70fa54ff8ba8cc0100`; four standard workflows (CI, Security, CodeQL, Repository Gate) passed on that SHA.
- Isolated regression results on the same SHA: focused Whisper/subprocess 17 passed; backend unit/security 303 passed, 3 skipped, 84 deselected; Worker contract 5 passed. These do not establish real Burmese speech accuracy or Windows-user-machine acceptance.
- Render auto-deploy remains disabled; latest live application-code SHA is `3b1b3766f2fb132bf4d80203e7174562f2879d9a`. Fresh read-only checks on 2026-10-13 passed: frontend root/assets HTTP 200, backend health/readiness HTTP 200, and CORS preflight for Render frontend plus existing Netlify origin. The docs-only SHA `8ab20000030b8f9931e3d488c4d31aa6a61147b5` passed CI [#38423887024](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38423887024), Security [#38423887084](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38423887084), CodeQL [#38423887068](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38423887068), and Repository Gate [#38423887059](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38423887059). No app redeploy, quota-consuming inference, paid worker provisioning, or production-data mutation was performed.
- Authenticated browser login/session/upload and real Burmese-media acceptance remain unverified; HTTP 200 alone is not user-journey proof.
- Highest-priority unresolved gates: (1) local real Burmese audio auto-detect vs forced-language comparison plus human review, subtitle playback and source integrity; (2) current Render health/readiness verification (tool access/logs did not establish current status); (3) explicit owner decisions for Netlify redeploy and any quota-consuming Whisper inference or paid persistent worker; (4) managed recovery, OAuth/Drive, SMTP, Stripe, Sentry, accessibility/performance, legal and independent security acceptance. Release remains **PENDING — NOT PRODUCTION READY**.

## Current repository checkpoint — 2026-10-11 UTC

- Source-code baseline reviewed for this reconciliation: e672bf0c5f75441e0bd9556db6811320a33a7a5e. The documentation updates in this sequence do not change application code; check the latest Actions run for the current documentation commit.
- Fresh CI [#38073711960](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073711960), Security [#38073711964](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073711964), CodeQL [#38073711959](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073711959), and Repository Gate [#38073711954](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073711954) passed on the earlier documentation checkpoint bbbf9d7bfd54517c011cdbcba20f987dcbdd8e75; the run SHA matched that checkpoint.
- The code baseline e672bf0c5f75441e0bd9556db6811320a33a7a5e separately passed CI [#38073136376](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073136376), Security [#38073136366](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073136366), CodeQL [#38073136341](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073136341), and Repository Gate [#38073136355](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073136355).
- Latest scheduled Kaggle dispatcher run [#38104412274](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38104412274) was skipped; it is not worker execution evidence. The dispatcher is intentionally opt-in and only useful when a due job exists.
- PRs #49–#53 added safeguards for Whisper quota reservation, Redis dispatch-lock ownership, SQL rollback before local Whisper fallback, opt-in Kaggle dispatch, and concurrent subscription bootstrap. PRs #54–#56 reconciled documentation; all four standard checks passed on the resulting main code baseline.
- These checks establish repository CI/security status only. They do not prove persistent worker service, real-media processing, authenticated Whisper inference, production storage/restore, OAuth/Drive, SMTP, Stripe, Sentry, full browser E2E, performance, accessibility, legal acceptance, or penetration testing.
- Release status remains **PENDING — NOT PRODUCTION READY**. No quota-consuming inference, paid worker/resource provisioning, production-data mutation, or destructive live drill without explicit owner approval.

> Owner: Project maintainers  
> Update when: requirements, phase status, gates, or release criteria change  
> Last Updated: 2026-10-11 UTC  
> Do NOT put here: provider secrets, detailed runbook commands, or unsupported live-health claims

## Authority

This is the **only master execution roadmap**. Supporting documents contain implementation-specific detail. Code existence is not production evidence. The detailed item-by-item checklist lives in [`docs/MASTER_REMAINING_WORK.md`](docs/MASTER_REMAINING_WORK.md); keep phase authority and execution priority here.

## Historical pre-PR #42/#43 main snapshot — 2026-10-10 UTC

- Current main SHA: `72154ae184f2316ee2c283be3184566edb91fe37` (PR #33 merge).
- PR #31 merged tenant-isolation negative cases for direct child-resource IDs. PR #32 merged storage lifecycle threshold/deletion-safety boundary tests (`a3ee23467ea2111e18b35523e698464d12c47024`). PR #33 merged a regression test proving asset metadata and audit history are preserved when storage-provider purge fails (`72154ae184f2316ee2c283be3184566edb91fe37`).
- PR-head checks for PR #32 and PR #33 passed, including backend, backend integration, E2E, CodeQL, Repository Gate, real-worker CI evidence, security scans, and local/Windows runtime/package smoke checks where present.
- Fresh main-SHA checks for `72154ae184f2316ee2c283be3184566edb91fe37` are still running; refresh them before describing the merged baseline as fully green.
- These changes improve automated regression coverage only. They do not establish live external-storage lifecycle/restore acceptance, a persistent production worker, authenticated real-audio Whisper inference, or full production end-to-end acceptance.
- Release status remains **PENDING — NOT PRODUCTION READY**. Do not run quota-consuming inference or provision billable worker capacity without explicit owner approval.

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

**Verification and evidence.** Main SHA `4dd3d4f0b761858c83047263a310dfa5429ab48b` includes merged PR #26 (SQLite restore integrity guard). Fresh CI, Security, CodeQL, Repository Gate, backup/restore, worker and Windows/local runtime evidence all passed on this SHA. See [`docs/MASTER_REMAINING_WORK.md`](docs/MASTER_REMAINING_WORK.md) for exact run links and scope limits; passing CI does not close live production gates.

Latest code/test update: PR #29 merged as `04bfedd5a79ee6eb90eaed83517c12c48282feb8`, expanding cross-tenant negative-case regression coverage. Its PR-head CI, security, CodeQL, worker evidence and repository gate passed; fresh main checks on this SHA are running. Details and scope limits are recorded in [`docs/MASTER_REMAINING_WORK.md`](docs/MASTER_REMAINING_WORK.md).

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
`apps/web-platform/backend/Dockerfile.worker` → Celery → Redis → PostgreSQL → FFmpeg/Whisper.

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
\n\n## Consolidated continuation roadmap — Phases 15–60\n\nThe canonical roadmap now incorporates the execution/evidence queue used by `PHASE_EXECUTION.md`. These phases are implementation continuations, not claims that the corresponding live gates are verified.\n\n### Phases 15–36\n15 cross-platform export preparation; 16 trend adapter; 17 A/B testing + feedback; 18 publishing metadata/idempotency; 19 trend connectors; 20 experiment registry; 21 AI quality/provider ranking; 22 EDL/FCPXML/NLE manifests; 23 storage lifecycle/DR; 24 SRE/incident/compliance; 25 character/style bible; 26 hook recommendation/episode scoring; 27 Burmese subtitle evaluation; 28 selective regeneration; 29 quota-aware scheduling; 30 human-review learning; 31 collaboration; 32 realtime/presence; 33 usage quotas; 34 enterprise tenant policy; 35 demo/onboarding/support; 36 launch gate/pen-test remediation.\n\n### Phases 37–45\n37 release train/migration safety; 38 cost governance; 39 data lifecycle/privacy; 40 DR automation; 41 multi-region readiness; 42 advanced queue scheduling; 43 evaluation dataset governance; 44 model/provider change management; 45 final operating maturity.\n\n### Phases 46–51 — implemented foundations\n46 evidence ledger; 47 provider acceptance matrix; 48 production E2E rehearsal seam; 49 billing/entitlement reconciliation; 50 release-candidate freeze; 51 final launch/post-launch watch.\n\nImplementation evidence now exists in `apps/web-platform/backend/app/services/release_maturity.py`, `app/models/core.py`, migration `0017_release_maturity`, unit tests, and `.github/workflows/repository-gate.yml`.\n\n**Important:** these are repository implementation foundations. They do not promote live worker/provider/billing/legal/security/manual gates to VERIFIED.\n\n### Phases 52–60 — pre-staged remaining backlog\n52 series trailer planning; 53 Burmese-first translation adapter; 54 sound/BGM workflow; 55 thumbnail candidate workflow; 56 LoRA/voice consistency seam; 57 social analytics import; 58 archive/cold-storage/PII purge; 59 Manual Mode production validation; 60 final UI/state/component audit.\n\nThe original requirements backlog remains covered: eight hook families, first-10-second structure, SEO metadata, retention/emotional arc, thumbnail 10→5 review, sound/BGM, subtitle styling, LoRA/voice consistency, Series Bible, five-episode planning, analytics/A-B feedback, video-generation fallback/watermark/commercial-use checks, quota accounting, subtitle correction metrics, social analytics import, archive/PII purge, backup/restore, monitoring/incident/on-call, and full testing/security/accessibility/legal/pen-test gates.\n\n### Execution rule\n\nCode-only foundations continue on `main` in parallel where independent. Live credentials, paid worker capacity, provider terms/limits, billing, legal/privacy approval, penetration testing, accessibility/manual acceptance, and real-media/browser evidence remain explicit gates. No secret is stored in the repository.

### Phases 61–68 — code-only foundations implemented
61 performance/cost optimization; 62 worker-fleet autoscaling; 63 content provenance/lineage; 64 advanced collaboration/enterprise audit; 65 provider adapter/marketplace seam; 66 localization quality operations; 67 monetization expansion; 68 post-launch SLO/error-budget operations.

Code-only foundations exist for phases 52–84 in `phase_52_60.py`, `phase_61_68.py`, `phase_69_76.py`, and `phase_77_84.py`, with corresponding unit tests. Treat these as implementation foundations only—not completed production features. Live runtime, provider, billing, privacy/legal, security, accessibility, and human acceptance gates remain open until separately evidenced.


## Phase 61–68 implementation evidence — 2026-10-08

Code-only foundations are now staged in `apps/web-platform/backend/app/services/phase_61_68.py` with unit coverage in `tests/test_phase_61_68.py`: performance/cost budgets, worker autoscaling policy, provenance lineage, enterprise permissions, provider capability discovery, localization quality thresholds, billing metering validation, SLO budgets and incident/rollback policy. Live telemetry, billing, provider, enterprise and post-launch acceptance remain external gates.


## Phase 69–76 implementation evidence — 2026-10-08

Code-only foundations are staged in `apps/web-platform/backend/app/services/phase_69_76.py` with unit coverage in `tests/test_phase_69_76.py`: rollout/cohort policy, schema-drift detection, restore verification, privacy-request closure, secret/config readiness, dependency-license allowlisting, chaos-drill acceptance, and deterministic release evidence packs. These contracts do not claim live backup, privacy/legal, secret-manager, license, chaos or release acceptance.

### Phase 69–76 queue
69 progressive rollout/cohort control; 70 schema/data-quality drift; 71 restore verification; 72 privacy/data-subject operations; 73 secret/config readiness; 74 dependency/license governance; 75 chaos/recovery drills; 76 final release evidence pack.


### Phases 77–84 — code-only foundations implemented
77 capacity/tenant quota forecasting; 78 API versioning/deprecation contracts; 79 migration retirement and data cleanup; 80 portable tenant export/import; 81 incident communications and status-page evidence; 82 support SLA/escalation operations; 83 provider marketplace billing/settlement seam; 84 final governance/ownership matrix and release evidence reconciliation.

Implementation rule: code-only foundations for phases 77–84 are present with unit tests. Any live provider, billing, legal, privacy, security, accessibility, human acceptance or production-runtime dependency remains an explicit external gate and is never inferred from unit tests.


## Phases 77–84 — code-only foundations complete

77 capacity/quota forecasting; 78 API versioning/deprecation; 79 migration retirement/data cleanup; 80 portable tenant export/import; 81 incident communications/status evidence; 82 support SLA/escalation; 83 provider settlement seam; 84 governance/ownership/evidence reconciliation.

Implementation is present in `phase_77_84.py` with unit coverage in `test_phase_77_84.py`. Live operational, provider, billing, privacy/legal, security and human acceptance gates remain separate and are not inferred from these tests.

## Future candidates after Phase 84 — unnumbered backlog

These candidates are not yet approved as numbered phases and should be prioritized only after the current release gates and product scope are reviewed:

- Windows desktop installer, first-run setup, update and uninstall lifecycle.
- Complete local media runtime/package parity: API, worker, FFmpeg, Whisper, ICU-dependent Burmese processing, database/storage and reproducible fixtures.
- AI model routing, provider health checks, tool calling, rate limits, and verified free-only fallback.
- Burmese quality evaluation and regression suite.
- Production LoRA/video generation only after provider terms, cost, legal, watermark and runtime acceptance.
- Direct social publishing and a full mobile client remain deferred unless explicitly reprioritized.

