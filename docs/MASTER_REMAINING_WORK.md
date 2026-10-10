# Narrativ Forge — Detailed Remaining Work Checklist

## Current repository checkpoint — 2026-10-11 UTC

- Current default-branch commit at this checkpoint: `e672bf0c5f75441e0bd9556db6811320a33a7a5e`.
- Fresh post-merge CI [38073136376](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073136376), Security [38073136366](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073136366), CodeQL [38073136341](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073136341), and Repository Gate [38073136355](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38073136355) all passed on this exact SHA.
- Cloudflare Whisper Preflight [38071946053](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38071946053) passed on parent SHA `1b6baad0df7f8b0ad5080381143288de62ba16a7` without audio or inference; do not treat it as a fresh preflight for `e672bf0`.
- Historical snapshots below are retained as history, not current-state claims. The current evidence does not prove authenticated provider inference, persistent worker availability, production storage lifecycle/restore, or external integration acceptance.
- Release remains **PENDING — NOT PRODUCTION READY**. Keep live Whisper inference, provider-quota consumption, paid worker capacity, production data changes, and other billable/destructive operations behind explicit approval.

> Companion checklist to `ROADMAP.md`; `ROADMAP.md` remains the sole master execution roadmap.
> Last reconciled: 2026-10-11 (UTC; refreshed after PR #56 and fresh main checks)
> Rule: never mark an item VERIFIED without evidence tied to the exact commit, environment, and run.
> Current release status: **PENDING — NOT PRODUCTION READY**.

## Historical pre-PR #42/#43 evidence snapshot — 2026-10-09 UTC

### Latest implementation change — cross-tenant negative-case coverage

- PR #29 merged as `04bfedd5a79ee6eb90eaed83517c12c48282feb8`: added integration/security regression coverage that a second tenant cannot read/update another tenant's Series or Episode, read/retry its ProcessingJob, or list its assets/scripts/scenes/subtitles through a foreign Episode ID.
- All PR #29 checks passed on head `dc50efba0fcb91aacee8b352ded5fe12f25deb78`, including [CI/E2E](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621252), [Security scans](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621363), [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/runs/113942806678), [Real Worker Evidence](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621352), and [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621184).
- Fresh main-SHA checks on `04bfedd5a79ee6eb90eaed83517c12c48282feb8` are running and must be refreshed before release acceptance: [CI #1225](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303768), [Security #990](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303785), [CodeQL #597](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303746), [Repository Gate #249](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303857), [Real Worker Evidence #193](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303703), [Windows Local Runtime #32](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303910), and [Windows Portable Package #33](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303824). [Local Runtime #35](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303748) has already passed.
- This is stronger automated tenant-isolation evidence, not a substitute for a full resource-by-resource audit or production browser E2E. Gate G11 remains open until broader role/membership/cross-tenant negative cases are accepted in the target environment.


- Main SHA `4dd3d4f0b761858c83047263a310dfa5429ab48b` (PR #26 merged) now has fresh passing checks: [CI #1217](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669315), [Security #982](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669353), [CodeQL #589](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669249), [Repository Gate #241](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669199), [Backup Restore Evidence #8](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669190), [Real Worker Evidence #191](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669286), [Local Runtime Evidence #33](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669461), [Windows Local Runtime #30](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669304), and [Windows Portable Package #31](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669256) all completed successfully.
- PR #26 merged as `4dd3d4f0b761858c83047263a310dfa5429ab48b`: SQLite restore now stages the backup and only replaces the target after `PRAGMA integrity_check` returns exactly `("ok",)`; regression tests preserve the existing target on failure. This is code/CI evidence, not a managed production database restore drill.
- On parent SHA `b231e2d7c2cf5b2114edcf4d9ecd2a59e509f7f0`, [CI](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092861), [Security](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092885), [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092877), and [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092923) passed.
- [Real Worker Evidence #190](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37963422875) passed in ephemeral CI (worker image, migration, local storage and synthetic media smoke). This does not establish a persistent production worker or live provider acceptance.
- [Cloudflare Whisper Preflight #2](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37964550063) passed as a non-inference preflight; authenticated real-audio transcription, VTT correctness, fallback and persistence remain open.
- [Kaggle Dispatcher #12](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37962902195) passed configuration/database checks but found no due `real_processing` jobs and did not launch a Kaggle session. Do not count this as Kaggle worker E2E.

## Latest main snapshot — 2026-10-10 UTC

- Current main SHA: `72154ae184f2316ee2c283be3184566edb91fe37` (PR #33 merge).
- PR #31 merged tenant-isolation negative cases for direct child-resource IDs. PR #32 merged storage lifecycle threshold/deletion-safety boundary tests (`a3ee23467ea2111e18b35523e698464d12c47024`). PR #33 merged a regression test proving asset metadata and audit history are preserved when storage-provider purge fails (`72154ae184f2316ee2c283be3184566edb91fe37`).
- PR-head checks for PR #32 and PR #33 passed, including backend, backend integration, E2E, CodeQL, Repository Gate, real-worker CI evidence, security scans, and local/Windows runtime/package smoke checks where present.
- Fresh main-SHA checks for `72154ae184f2316ee2c283be3184566edb91fe37` are still running; refresh them before describing the merged baseline as fully green.
- These changes improve automated regression coverage only. They do not establish live external-storage lifecycle/restore acceptance, a persistent production worker, authenticated real-audio Whisper inference, or full production end-to-end acceptance.
- Release status remains **PENDING — NOT PRODUCTION READY**. Do not run quota-consuming inference or provision billable worker capacity without explicit owner approval.

## How to use this checklist

Use these status labels consistently:

- `TODO` — not started or no reliable current evidence.
- `IN PROGRESS` — actively being worked on.
- `VERIFY` — code/config may exist; evidence must be refreshed.
- `BLOCKED` — cannot proceed until the listed dependency is resolved.
- `OWNER ACTION` — requires a user/maintainer decision, credential setup, provider console, sample media, or approval.
- `EXTERNAL ACTION` — requires an independent provider, legal/security reviewer, or external service.
- `VERIFIED` — passed with a link to current evidence and exact SHA.
- `DEFERRED` — intentionally postponed with a reason.

Do not equate implemented code, passing unit tests, deployed service reachability, or configured secrets with end-to-end production acceptance.

## 1. Immediate cloud/repository queue

### 1.1 Establish an exact baseline
- [x] Read the current roadmap and current-state documents.
- [x] Inspect open PRs #23 and #24 and recent main-branch workflow runs.
- [x] Record that inspected main SHA `1e468adf215c12dcb2314ff7aff948c426f2bfb9` had successful CI, Security, CodeQL, and Repository Gate runs on 2026-10-09; subsequent main commits require fresh checks.
- [x] Re-check main SHA and latest checks immediately before merge decisions.
- [x] Inspect PR #24 diff, existing checks, model allowlist, no-paid-fallback guarantees, tests, and documentation consistency.
- [x] PR #24 follow-up: removed Thinking Machines Inkling/Inkling Small from the direct chat-completions allowlist because they are intended for agentic harnesses; added a regression test and clarified the model audit.
- [x] PR #24 security follow-up: pinned the OpenRouter route to HTTPS `openrouter.ai/api/v1` so a custom compatible URL cannot receive the OpenRouter API key; added negative tests for HTTP, foreign hosts, deceptive hosts, URL credentials, and wrong paths.
- [x] PR #24 merged as `3cffc55c5ab96c164e89af37a13a58b03ef4c9cc` after its exact head `2dad26e037b35b5f6726f2cf036e7047395d625c` passed CI, backend integration, E2E, Security, CodeQL, Repository Gate, real-worker E2E, local runtime, Windows local runtime and Windows package evidence.
- [x] Inspect PR #23 diff, required checks, safe GET-only preflight, diagnostics redaction, workflow permissions, and documentation consistency.
- [x] PR #23 merged as `6eaa41668d0d49d4380c0bb2a9e3a1e6f2122ce2` after its PR-head CI, backend integration, E2E, Security, CodeQL and Repository Gate checks passed.
- [x] Run the manual **Cloudflare Whisper Preflight** at exact SHA `4ec6a36adb1014f116f51aaa9dedd546132a7a30`; run [#37949775861](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37949775861) and [redacted evidence artifact](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37949775861/artifacts/11625716148) confirm the unauthenticated GET reached the Worker JSON method guard (HTTP 405, `Method not allowed`). No audio or Workers AI inference was attempted; evidence explicitly records `production_verified=false`.
- [x] Resolve PR review/check failures before merge; no failed required checks remained on either PR head at merge time.
- [x] Verify main SHA `4ec6a36adb1014f116f51aaa9dedd546132a7a30` after PR #23 merge and the checklist update: [CI](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37948941340), [Security](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37948941603), [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37948941526), and [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37948941277) all completed successfully. Any later commit requires fresh checks.

### 1.2 Worker and media pipeline
- [x] Follow-up [Kaggle Dispatcher #12](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37962902195) on `b231e2d` passed configuration and database checks; it found no due `real_processing` jobs, so it intentionally did not launch Kaggle. Dispatcher code/config checks are verified; actual Kaggle execution and completed media processing are not.
- [ ] Audit `web-platform/backend/Dockerfile.worker`, Celery registration, Redis queue, PostgreSQL state, FFmpeg/Whisper availability, retry policy, DLQ, late ACK, duplicate dispatch, stale-job recovery, and shutdown behavior.
- [x] [Real Worker Evidence #190](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37963422875) passed on `b231e2d`: worker image build, migrations, local storage permissions, Celery readiness, and synthetic media smoke succeeded in an isolated CI environment.
- [x] Worker Docker build and Alembic migration CI step passed in that run; refresh evidence after every later worker/runtime code change.
- [x] PostgreSQL/Redis-backed integration and worker smoke checks passed in isolated CI; persistent production worker, external storage, and representative user-media acceptance remain open.
- [ ] Verify representative media: upload → enqueue → worker → FFmpeg → Whisper → subtitles/VTT → DB/storage → UI.
- [ ] Run retry, DLQ, duplicate-dispatch, worker-loss, timeout, and recovery drills.
- [ ] Provision a continuously running worker runtime only after the owner explicitly approves any cost; current Render Free web service is not a background worker.
- [ ] Keep production readiness blocked until live worker evidence exists.

### 1.3 OpenRouter free-only route
- [ ] Verify the exact approved chat-model allowlist and the behavior of `openrouter/free`.
- [ ] Ensure arbitrary IDs, unapproved IDs, and paid fallbacks are rejected even if an ID contains a `:free` suffix.
- [ ] Verify missing/invalid key and endpoint-unavailable behavior, including deterministic Mock AI fallback.
- [ ] Ensure authentication errors do not trigger paid inference and other provider keys are not silently used by this route.
- [ ] Run tests on the PR and exact merged SHA.
- [ ] Verify a controlled real request only after the owner has configured a valid key; never reveal or commit the key.
- [ ] Recheck current model availability, chat capability, free status, terms, quota, and sunset notices before describing a model as usable.

### 1.4 Cloudflare Whisper 403
- [x] PR #23 changes and workflow checks were reviewed and merged.
- [x] [Cloudflare Whisper Preflight #2](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37964550063) passed on `b231e2d` as a non-inference GET/method-guard check.
- [x] Preflight evidence exists; it proves only the method-guard/deployment contract, not authenticated audio transcription, subtitle persistence, fallback or quota accounting.
- [ ] Do not send audio, invoke Workers AI, change production secrets, or deploy a Worker without explicit approval.
- [ ] After approved deployment/configuration, test authenticated real-audio transcription, VTT correctness, usage idempotency, fallback, and persistence.

### 1.5 Repo documentation and evidence ledger
- [ ] Keep `ROADMAP.md`, `CURRENT_STATE.md`, `PHASE_EXECUTION.md`, `README.md`, `docs/OWNER_ACTION_CHECKLIST.md`, and this checklist consistent.
- [ ] For each verification, record commit SHA, workflow/run URL, environment, timestamp, artifact/result, owner, status, and any expiry/retest date.
- [ ] Keep credentials and secret values out of docs, logs, PR comments, and generated evidence.
- [ ] Keep unresolved items as TODO/VERIFY/BLOCKED/OWNER ACTION/EXTERNAL ACTION rather than silently marking complete.

## 2. Production release gates

- [ ] **G1 — Real media pipeline:** upload → queue → worker → FFmpeg/Whisper → subtitle/VTT → database and storage.
- [ ] **G2 — Queue resilience:** retries, DLQ, duplicate dispatch, worker loss, stale jobs, timeouts, and failover.
- [ ] **G3 — Storage lifecycle:** live upload/download/delete/archive/restore across each configured B2/Supabase/Cloudinary provider.
- [ ] **G4 — Whisper integration:** authenticated real-audio transcription, VTT/subtitle correctness, usage idempotency, fallback and persistence.
- [ ] **G5 — Google OAuth/Drive:** real login, export, token refresh, recovery, and idempotent handling.
- [ ] **G6 — SMTP:** real test-mail delivery, failure behavior, and sender/configuration validation.
- [ ] **G7 — Stripe:** test checkout, webhook signature, idempotency, entitlement changes, and usage/billing reconciliation.
- [ ] **G8 — Sentry:** intentionally trigger a safe test event and verify event receipt and alert routing.
- [ ] **G9 — Database migrations:** query the live target and record exact Alembic head; external DB access currently limits verification.
- [ ] **G10 — Backup/restore:** backup and restore a managed database in an isolated target; verify schema, row counts/integrity, and application readiness.
- [ ] **G11 — Auth/tenant isolation:** browser E2E for multi-membership organization selection, roles, and cross-tenant resource denial.
- [ ] **G12 — Full E2E/performance:** representative browser workflow, load/performance baseline, and failure recovery.
- [ ] **G13 — Security:** dependency, container, CodeQL, secret scanning and relevant security artifacts tied to the release SHA.
- [ ] **G14 — Accessibility/responsive:** automated and manual WCAG 2.2 AA-oriented checks for key screens, keyboard, focus, contrast, responsive states and error handling.
- [ ] **G15 — Legal/privacy/compliance:** owner/legal sign-off for privacy, retention, processing, and data handling.
- [ ] **G16 — Pen-test:** independent test, documented findings, remediation, and retest.
- [ ] **G17 — Provider acceptance:** current limits, quota, commercial-use rights, watermarks, retention, fallback, and provider terms reviewed for every production integration.

## 3. Cloud-side engineering audits

- [ ] Tenant context and organization selection for users with multiple memberships.
- [ ] Resource-by-resource tenant authorization review; prove negative cases with tests.
- [ ] Backup/restore automation, integrity checks, retention and cleanup evidence.
- [ ] Credentialed verification workflow framework: manual approval, secret redaction, ephemeral setup, safe cleanup, and artifacts.
- [ ] Provider acceptance matrix: credentials dependency, quota, terms, fallback, commercial-use/watermark rights, and last-verified date.
- [ ] Release/migration/rollback/freeze/launch eligibility criteria.
- [ ] Config/secrets readiness checks that never reveal secret values.
- [ ] Dependency/license governance and software supply-chain evidence.
- [ ] Schema drift detection, restore verification, chaos/recovery drills, and data-quality checks.
- [ ] Release evidence pack for exact SHA, CI, security, migrations, E2E, provider acceptance and sign-offs.
- [ ] API versioning/deprecation, portable tenant export/import, incident communications, support escalation and ownership evidence.

## 4. Product roadmap — Phases 13–36

These are product/engineering workstreams, not proof that the production gates above are satisfied.

- [ ] **13 — Cross-platform export preparation:** TikTok, YouTube Shorts, Facebook Reels, Instagram Reels; preparation only, no direct publishing.
- [ ] **14 — Trend integration adapter.**
- [ ] **15 — A/B testing and feedback loop.**
- [ ] **16 — Series trailer planning.**
- [ ] **17 — Burmese-first translation adapter.**
- [ ] **18 — Publishing metadata, preparation adapters, idempotency.**
- [ ] **19 — Trend connectors and quota management.**
- [ ] **20 — Experiment registry.**
- [ ] **21 — AI quality evaluation and provider ranking.**
- [ ] **22 — EDL/FCPXML/NLE manifests.**
- [ ] **23 — Storage lifecycle and disaster recovery.**
- [ ] **24 — SRE, incident response and compliance foundations.**
- [ ] **25 — Character/style Bible.**
- [ ] **26 — Hook recommendation and episode scoring.**
- [ ] **27 — Burmese subtitle evaluation.**
- [ ] **28 — Selective regeneration.**
- [ ] **29 — Quota-aware scheduling.**
- [ ] **30 — Human-review learning.**
- [ ] **31 — Collaboration foundations.**
- [ ] **32 — Realtime notifications/presence.**
- [ ] **33 — Usage quotas.**
- [ ] **34 — Enterprise tenant policy.**
- [ ] **35 — Demo, onboarding and support foundations.**
- [ ] **36 — Launch gate and penetration-test remediation.**

## 5. Operational maturity — Phases 37–60

- [ ] **37 — Release train and migration safety.**
- [ ] **38 — Cost governance.**
- [ ] **39 — Data lifecycle and privacy.**
- [ ] **40 — Disaster-recovery automation.**
- [ ] **41 — Multi-region readiness.**
- [ ] **42 — Advanced queue scheduling.**
- [ ] **43 — Evaluation dataset governance.**
- [ ] **44 — Model/provider change management.**
- [ ] **45 — Operating maturity.**
- [ ] **46 — Evidence ledger.**
- [ ] **47 — Provider acceptance matrix.**
- [ ] **48 — Production E2E rehearsal.**
- [ ] **49 — Billing/entitlement reconciliation.**
- [ ] **50 — Release-candidate freeze.**
- [ ] **51 — Launch and post-launch watch.**
- [ ] **52 — Series trailer planning follow-through.**
- [ ] **53 — Burmese translation adapter follow-through.**
- [ ] **54 — Sound/BGM workflow.**
- [ ] **55 — Thumbnail workflow: generate 10 candidates → shortlist 5 usable → human selects final.**
- [ ] **56 — LoRA/voice consistency, only with provider/legal/runtime acceptance.**
- [ ] **57 — Social analytics import.**
- [ ] **58 — Archive/cold storage/PII purge.**
- [ ] **59 — Manual Mode production validation.**
- [ ] **60 — Final UI/state/component audit.**

## 6. Future maturity — Phases 61–84

Existing code/tests may provide foundations. Audit what is already implemented before creating duplicate systems; live acceptance is separate.

- [ ] **61 — Performance and cost optimization.**
- [ ] **62 — Worker-fleet autoscaling.**
- [ ] **63 — Content provenance and lineage.**
- [ ] **64 — Advanced collaboration and enterprise audit.**
- [ ] **65 — Provider adapter/marketplace seam.**
- [ ] **66 — Localization quality operations.**
- [ ] **67 — Monetization expansion.**
- [ ] **68 — SLO/error-budget operations.**
- [ ] **69 — Progressive rollout/cohort control.**
- [ ] **70 — Schema/data-quality drift.**
- [ ] **71 — Restore verification.**
- [ ] **72 — Privacy/data-subject operations.**
- [ ] **73 — Secret/config readiness.**
- [ ] **74 — Dependency/license governance.**
- [ ] **75 — Chaos/recovery drills.**
- [ ] **76 — Final release evidence pack.**
- [ ] **77 — Capacity/tenant quota forecasting.**
- [ ] **78 — API versioning/deprecation.**
- [ ] **79 — Migration retirement/data cleanup.**
- [ ] **80 — Portable tenant export/import.**
- [ ] **81 — Incident communications/status-page evidence.**
- [ ] **82 — Support SLA/escalation.**
- [ ] **83 — Provider marketplace billing/settlement seam.**
- [ ] **84 — Governance/ownership/evidence reconciliation.**

## 7. Product requirements that must not be lost

- [ ] Story ingestion → AI episode split → human approval.
- [ ] Eight hook families: Question, Shock, Mystery, Warning, Personal Story, Contrarian, Cliffhanger, Number.
- [ ] First 10 seconds: Hook → Pattern Interrupt → Context → Content.
- [ ] SEO title/caption/hashtags/keywords/posting-time logic.
- [ ] Retention, emotional arc, cliffhanger/recap, engagement triggers.
- [ ] Thumbnail candidate workflow (10 candidates → 5 usable → human selection).
- [ ] Sound/BGM workflow and subtitle styling.
- [ ] Series Bible, character/style/voice consistency and continuity checks.
- [ ] Five-episode batch planning/calendar.
- [ ] Analytics feedback and evidence-based A/B learning.
- [ ] Subtitle correction history, metrics and evaluation export.
- [ ] Video-generation adapter/fallback with watermark/commercial-use checks.
- [ ] Provider quota accounting and live limit verification.
- [ ] Social analytics import; archive/cold storage/PII purge.
- [ ] Monitoring, incident response, backup/restore and rollback.

## 8. Future candidates after Phase 84 (not yet approved numbered phases)

- [ ] Windows desktop installer, first-run setup, updates and uninstall.
- [ ] Local media runtime: API, worker, FFmpeg, Whisper, DB/storage.
- [ ] Cloud/local behavior parity and reproducible local test fixtures.
- [ ] Convert portable ZIP into a real installer only after resolving current omissions: worker, FFmpeg/Whisper and ICU-dependent Burmese processing; document Python 3.12, Node.js 20 and first-run internet requirements.
- [ ] AI model routing, health checks, tool calling, rate limits and fallback with free-only verification.
- [ ] Burmese quality evaluation/regression suite.
- [ ] Production LoRA/video-generation only after provider, legal, cost, watermark and runtime acceptance.
- [ ] Direct social publishing remains deferred; full mobile client remains deferred unless explicitly reprioritized.

## 9. Owner / external actions

- [ ] Owner configures OpenRouter key directly in the intended secret manager; never paste it into chat or commit it.
- [ ] Owner decides whether to approve a paid worker or identify an equivalent continuously running worker runtime.
- [ ] Owner supplies provider credentials as needed (storage, Google OAuth, SMTP, Stripe, Sentry, Cloudflare) through secret managers only.
- [ ] Owner supplies representative, permitted media samples for Burmese transcription/subtitle/pipeline acceptance.
- [ ] Owner/human reviewer accepts Manual Mode, UI, thumbnails, translation and media output.
- [ ] Owner/legal reviewer signs off on privacy, retention, provider terms and commercial-use rights.
- [ ] External tester performs penetration test and retest.
- [ ] Authorized staging/production database access is arranged for migration and backup/restore evidence.

Safety rules: no secrets in repository or chat; no destructive tests on production; no billable or quota-consuming actions and no production deployments without explicit approval.

## 10. Manual Mode evidence gate

Before Manual Mode can be called production-ready, collect:
- [ ] 15–20 representative manual videos.
- [ ] Production logs and time measurements.
- [ ] Multiple hook types and subtitle styles.
- [ ] Commercial-use review.
- [ ] Repeated-problem dataset and human feedback.
- [ ] MVP scope freeze and owner acceptance.

## 11. Completion definitions

- **Implemented:** code exists.
- **CI verified:** relevant automated tests pass on the exact SHA.
- **Live verified:** the actual provider/runtime was exercised and evidence is linked.
- **Externally approved:** required owner/legal/security/human sign-off is recorded.
- **Blocked/deferred:** reason and unblock condition are documented.
- **Production Ready:** all applicable release gates have fresh evidence; no blocker is hidden by a successful unit test or healthy API endpoint.

## 12. One-at-a-time execution order

1. Establish current repository/PR/check baseline and keep this checklist synchronized; PRs #23, #24, #26, and #27 are already merged.
2. Wait for and inspect every fresh workflow on main SHA `4dd3d4f0b761858c83047263a310dfa5429ab48b`; fix any reproducible failures and rerun affected checks.
3. Refresh this evidence ledger and the current-state/roadmap docs with exact run URLs and scope limitations.
4. Continue cloud-only code gaps and automated evidence in parallel where tasks are independent (tests, security/dependency scans, runtime smoke, docs/evidence).
5. Complete non-billable provider checks first; keep authenticated inference, paid compute, production deployment, and quota-consuming tests gated by explicit owner approval.
6. Complete live release gates in dependency order and record exact environment, SHA, run/deploy ID, result, artifact and timestamp.
7. Identify owner/external blockers only when code-side work and safe automation are exhausted.
8. Perform final release audit; production remains blocked until all applicable gates have fresh evidence and approvals.
9. **Only after cloud-side work is exhausted and verified, begin Windows Local setup.**
