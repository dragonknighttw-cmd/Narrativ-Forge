# Authoritative checkpoint — 2026-10-16 UTC (Local Verification & Decoupling)

- **Standalone runtime decoupling:** Port 3001 assigned to Next.js Web Studio; Port 8001 assigned to FastAPI Backend; Port 8082 assigned to Expo Mobile Reviewer.
- **Backend operational verification:** FastAPI API executed locally via isolated test suite. `GET /api/v1/health` and `GET /` returned `HTTP 200 OK` (`{'status': 'ok', 'service': 'narrativ-forge-api'}`).
- **Frontend enhancement:** Proportional Multi-Track Visual Timeline Preview strip implemented in `apps/web-platform/frontend/app/episodes/[id]/scenes/page.tsx` displaying visual lanes for Script, Scene Prompts, Voiceover, and Audio. TypeScript typecheck passed with 0 errors (`npx tsc --noEmit`).
- **Documentation consolidation:** Consolidated 10 fragmented legacy numbered documentation drafts (`01-product.md` through `21-master-completion-matrix.md`) into `archive/legacy_numbered/`. Rewrote `ROADMAP.md` completely in English, synchronizing all 243 legacy extracted backlog items into 5 prioritized categories.
- **Release status:** **LOCAL STANDALONE VERIFIED; CLOUD RELEASE PENDING.** Live Cloudflare Whisper dialect ASR verification, Redis worker heartbeats, and Render cloud sync remain pending.

---

# Authoritative checkpoint — 2026-10-15 UTC

- **Latest application-code commit observed:** `d370921054b92bbc89b5cf647680543f714c906d` (2026-10-14 17:17:39 UTC).
- **Infrastructure audit:** [INFRASTRUCTURE_AUDIT.md](INFRASTRUCTURE_AUDIT.md). Render API and frontend services have successful listed deploys, but both are still on `3b1b3766f2fb132bf4d80203e7174562f2879d9a`; auto-deploy is disabled, so hosted services lag repository head.
- **Provider findings:** two active Supabase projects require canonical-target confirmation; security advisor reported 40 RLS/no-policy findings on `Narrativ-Forge` and an exposed SECURITY DEFINER function on `Narrativ-Forge-1`; Cloudflare lists edge and Whisper Workers, but live authenticated media acceptance remains unverified.
- **Release:** **PENDING — NOT PRODUCTION READY.** Do not redeploy or mutate schema until exact-head CI, canonical database/frontend confirmation, security review, and owner-approved release gates pass.

The checkpoints below are historical; use this block for current audit findings. See [ROADMAP.md](ROADMAP.md) and [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

# Authoritative checkpoint — 2026-10-14 UTC

- **Base main SHA for this checkpoint:** `4959810fc1a7449cc714084ca0169557dce02513`.
- **Application fix and repository hygiene:** PR #77 fixes the review approval timestamp bug; PR #80 removes the generated TypeScript build cache from version control and ignores `*.tsbuildinfo`.
- **Merged feature acceptance:** PR #83 persists Series Bible characters with tenant-scoped API/database storage; PR #84 adds continuity tests; PR #85 tests subtitle tenant boundaries, viewer write denial, and approved-content immutability; PR #86 tests Script Studio optimistic locking/history and scene/script scope; PR #88 tests Series Bible UI persistence after reload; PR #89 verifies uploaded source SHA-256/size, processed output integrity, mock processing completion, and subtitle SRT export.
- **Exact-head checks passed:** PRs #85 and #86 passed backend/integration, frontend, E2E, CodeQL/security, runtime/package, and Real Worker Evidence. PRs #88 and #89 passed their applicable frontend E2E, backend/integration, CodeQL/security, runtime/package, and repository checks. PR #89 backend: **309 passed, 3 skipped**; integration: **75 passed, 1 skipped**; E2E: **4 passed**.
- **Burmese ASR remains unaccepted.** The human-quality gate still needs a dialect-specific reference transcript and human review. Prior local results produced no Myanmar-script output in the tested configurations. Passing mock processing, subtitle export, or CI worker smoke does not establish transcript quality.
- **Remaining external/workflow gates:** authenticated non-mock media E2E with real source media and provider behavior; asset/processing error/retry acceptance; managed restore and provider integration; accessibility, privacy/legal/commercial-use, and independent security sign-offs.
- **Release:** **PENDING — NOT PRODUCTION READY.** No production deployment, paid resource provisioning, production-data mutation, or cloud inference/quota use. Human local ASR/media-quality acceptance remains deferred.

The older checkpoint notes below are historical. Use this section as the current status at the base SHA above.


---

# Current verified checkpoint — 2026-10-14 UTC

- **Base main SHA for this checkpoint:** `d6709d8b84d66f019015db9d6a9010ce9e923ccb` (after PRs #79 and #80; PR #81 refreshes this documentation).
- **Latest application-code fix:** `6dbd4fabe715c06b565c6e53cf187b7373bbb9df`, merged in [PR #77](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/77). The undefined `approved_at` bug is fixed: one UTC timestamp is assigned and reused for the review record and response. [Issue #76](https://github.com/dragonknighttw-cmd/Narrativ-Forge/issues/76) is closed.
- **Fix verification on exact candidate SHA** `a05a97752a30889d691c687ea47b519a089e7e6b`: CI passed (backend unit/security **303 passed, 3 skipped**; PostgreSQL/Redis integration **72 passed, 1 skipped**; frontend, E2E and Worker contract tests passed). Security, CodeQL, Repository Gate, Local Runtime Evidence, Windows Local Runtime Evidence, Windows Portable Package Evidence, and Real Worker Evidence all passed. The merged commit contains the same code/test patch.
- **Documentation status reconciliation:** [PR #79](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/79) merged; repository hygiene [PR #80](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/80) also merged. The tracked TypeScript incremental cache was removed and `*.tsbuildinfo` is now ignored. Historical sections below are checkpoints and may describe earlier SHAs/status; use this top block for current status.
- **Still blocked:** Burmese real-speech quality acceptance (local report tested older SHA and got 0 Myanmar-script characters from three Whisper configurations), focused acceptance of overnight feature workflows, authenticated local/staging media E2E, external provider/backup/restore verification, accessibility/legal/privacy and owner/security sign-off.
- No production deployment, paid resource provisioning, production-data mutation, or cloud inference was performed as part of these changes. **Release remains PENDING — NOT PRODUCTION READY.**

## Next actions

1. Run/record focused acceptance for batch generation, Script Studio to scene planning, thumbnail approval, subtitle editing/preview, asset validation, processing state, Series Bible, and tenant/role guards.
2. Keep Burmese ASR unaccepted until a human reviews dialect/reference transcript and a usable transcript passes quality checks; no cloud inference without approval.
3. Decide whether generated `apps/web-platform/frontend/tsconfig.tsbuildinfo` should remain tracked.
4. Complete safe local/staging upload/playback/source-integrity E2E and the remaining external release gates: managed restore, provider integrations, performance, accessibility, legal/privacy/commercial use, and independent security review.
5. Do not deploy production or provision billable capacity without explicit owner approval.

---

## Latest main + overnight-work reconciliation — 2026-10-14 UTC

- **Default branch snapshot:** `main` at `fe17d74229cb51ca4eec125b720594fb85ebbbb6` (latest observed commit: generated frontend `tsconfig.tsbuildinfo`).
- **Latest application-code checkpoint:** `f2f45cfca45f6e36408a8674d3d96eaec61c8fd2`. The three feature commits `6a6f54e`, `67deb66`, and `f2f45cf` added core platform workflows; commits after that code checkpoint are documentation/roadmap reconciliation plus the generated TypeScript build-info file.
- **Newly recorded implementation scope:** 8 Burmese hook families; 5-episode batch generator; Script Studio assistant and scene auto-planning; thumbnail generation/shortlisting/human approval workflow; subtitle cue editing and keyboard shortcuts; 9:16 subtitle preview/safe-zone simulator; asset library guidance/filtering; processing stepper; Series Bible; Burmese typography/mobile navigation; and a 512-dimension mock RAG/semantic-search foundation.
- **Evidence boundary:** repository state records 12 focused backend unit tests and frontend `tsc --noEmit` as passing. The latest main SHA's CI, Security, CodeQL and Repository Gate conclusions were not independently available from the status connector during this reconciliation; rerun/check exact-SHA Actions before treating the current head as green.
- **Local Burmese ASR acceptance (operator report, 2026-10-13):** tested older application SHA `3b1b3766f2fb132bf4d80203e7174562f2879d9a`, not the new feature SHA. On the same source audio, Whisper small auto-detect, small forced Burmese and large-v3-turbo all emitted non-Myanmar scripts/text (0 Myanmar-script characters); all were correctly rejected as `ASR_LANGUAGE_MISMATCH`. Local focused Whisper/subprocess tests: 15 passed, 2 skipped; unit: 281 passed, 5 skipped; unit/security: 301 passed, 5 skipped. No Cloudflare inference/quota was used. This is a **Burmese quality failure**, not a successful ASR acceptance. Re-run relevant regression tests on current code and obtain human dialect/reference-transcript review before choosing a model/parameter change.
- **Confirmed release-blocking code defect (not fixed here):** current `apps/web-platform/backend/app/api/routes/review.py` defines `approve_review()` but its return references `approved_at.isoformat()` without defining `approved_at` in that function. The approval request can therefore raise `NameError` after the DB commit. This documentation-only PR records the blocker; application code remains unchanged.
- **Build artifact hygiene:** `apps/web-platform/frontend/tsconfig.tsbuildinfo` is tracked by the latest commit. Decide whether it should be ignored/removed as generated output; do not treat it as a feature.
- **Deployment boundary:** current main is ahead of the deployed application baseline `3b1b3766`; Render auto-deploy is documented as disabled in the latest live checkpoint. Do not infer the new features are deployed. No deploy, paid worker provisioning, quota-consuming inference or production-data mutation was performed.
- **Release:** **PENDING — NOT PRODUCTION READY**.

### Reconciled next actions (in priority order)

1. Fix and regression-test the confirmed `approve_review()` undefined `approved_at` defect in a separate code change; this plan-only PR does not change application code.
2. Check exact-SHA CI, Security, CodeQL and Repository Gate on the latest feature-bearing main head; refresh the evidence after the documentation-only plan update.
3. Run focused API/UI acceptance for batch generation, script-to-scene planning, thumbnail approval, subtitle editing/preview, asset validation, and tenant/role authorization. Confirm persistence and human-review gates, not just component presence.
4. Re-run ASR guard/subprocess regression tests on the current code SHA. Keep real Burmese audio acceptance open until a human confirms dialect/reference transcript and a model produces a reviewed, usable transcript.
5. Complete browser login/session/upload and real-media subtitle timing/playback/source-integrity checks in a safe local/staging environment.
6. Keep continuous worker, managed full-schema restore, live provider/storage/OAuth/Drive/SMTP/Stripe/Sentry, performance/load, accessibility, legal/privacy/commercial-use review, and independent penetration testing as explicit external acceptance gates.
7. Decide whether to ignore the generated `tsconfig.tsbuildinfo`; then update the canonical plan/evidence with the resulting decision.
8. Only after the above gates and owner decisions, consider deployment/release. Do not spend quota or create billable capacity without explicit approval.

## Previous post-merge checkpoint — 2026-10-13 UTC

- PR #73 (Burmese ASR script guard) merged as `c04a17d76f7f2ee42a8ad9a0fff620c9af75b869`; PR #72 (cloud status/report refresh) merged as `dfff46a5335833723e403b70fa54ff8ba8cc0100`.
- Application-code checkpoint after both merges: `dfff46a5335833723e403b70fa54ff8ba8cc0100`. The documentation reconciliation preceding this update was `49dcacb25d88a5f4b78a6aa287245fc0c53978ed`; this change is documentation-only.
- CI, Security, CodeQL and Repository Gate passed on the application-code checkpoint. An isolated Linux workspace at that exact SHA also passed focused Whisper/subprocess tests (17), backend unit/security selection (303 passed, 3 skipped, 84 deselected), and Worker contract tests (5).
- Render remains free-tier with auto-deploy disabled. Fresh read-only live checks on 2026-10-13 passed: frontend root/assets HTTP 200; backend `/api/v1/health` and `/api/v1/ready` HTTP 200; CORS preflight passed for Render frontend and existing Netlify origin, including auth/upload/episode routes. These are reachability/preflight checks, not authenticated browser E2E. Latest live application-code SHA is `3b1b3766f2fb132bf4d80203e7174562f2879d9a`; docs-only commits were not deployed. Standard workflows passed on docs SHA `8ab20000030b8f9931e3d488c4d31aa6a61147b5`.
- Docs-only main SHA `8ab20000030b8f9931e3d488c4d31aa6a61147b5` has passing CI, Security, CodeQL, and Repository Gate; no application deploy was made.
- Release remains **PENDING — NOT PRODUCTION READY**. Real Burmese-audio comparison, human transcript review, subtitle playback/timing and source-media integrity are still unverified; do not infer them from CI or the Myanmar-script guard.

## Current checkpoint — 2026-10-11 UTC

- The direct-main implementation commit `df22942f3482690eae79859670581908df26b360` fixes the FFmpeg/WASM loader retry defect: failed initialization clears the rejected cached promise so a later attempt can retry.
- **Windows local Unicode media runtime — VERIFIED for local synthetic scope (2026-10-12 local):** `unicode_nfc_only` is explicit in settings, API metadata, and tests; backend requirements no longer include PyICU/myanmartools. Wheel-only installation, D-drive SQLite migration to `0018_tenant_backfill_guard`, seven-check preflight, and canonical Celery worker smoke passed using Memurai 6380, local FFmpeg, Whisper tiny, and local storage. The final smoke uploaded its generated video through the local storage provider; job `ffe5abb2-193c-47a3-a976-110ca18d54e8` completed at 100%, with input/output/transcript assets and a subtitle record persisted. The tone fixture contains no speech, so Whisper's transcript has zero segments and the worker-created subtitle has zero cues. A separate deterministic Unicode transcript fixture traversed the canonical subtitle generator and produced normalized U+1026 plus an SRT file; API subtitle generation/export also passed. Focused tests: 10 passed. Full backend unit selection: 260 passed, 5 skipped, 103 deselected, 1 unrelated Windows SQLite restore file-lock failure. Worker process shut down; this is not production/provider or Burmese speech-quality verification. Details and exact artifacts: [docs/LOCAL_RUNTIME.md](./docs/LOCAL_RUNTIME.md) and [local runtime report](./docs/Report/LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md).
- Fresh exact-SHA checks passed on that implementation commit:
  - [CI #38134796964](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38134796964) — frontend typecheck/build, backend unit/security tests, PostgreSQL/Redis integration, and browser E2E passed.
  - [Security #38134796869](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38134796869) — dependency audit, SAST, and container scan passed.
  - [CodeQL #38134796898](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38134796898) — Python and JavaScript/TypeScript analysis passed.
  - [Repository Gate #38134796867](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38134796867) passed.
  - [Local Runtime Evidence #38134796862](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38134796862) passed.
  - [Windows Portable Package Evidence #38134796875](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38134796875) passed, including packaged ZIP install/restart, data persistence, and cleanup smoke.

- The previous audit base `9b65b851b2151437354269730a586a82883142a4` was documentation-only; no open pull requests were present at that audit point. This repository now defaults to direct-main changes for user-requested work, without creating feature branches or PRs unless explicitly requested.
- The last application-code worker baseline is `e0ce675ea27f3b6d5aa4bb53e8a2bf5bb6698775`. [Real Worker Evidence #38129952195](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38129952195) passed on that SHA. Its artifact records ephemeral PostgreSQL 16 + Redis 7 worker build/startup, migrations, storage access, retry/DLQ/tenant integration, and generated synthetic-media processing through processed video, transcript, and subtitle output. This is **ephemeral worker evidence**, not proof of a continuously running production worker or live-provider processing.
- [Application Schema Restore Evidence #38132450389](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38132450389) passed on `e96f26ef3b2f132d46bc95e87b28909de654a3f4`: full Alembic migrations on ephemeral PostgreSQL 17, backup, restore into a fresh database, schema/migration-head comparison, and synthetic sentinel check. This is **ephemeral CI** restore evidence, not a managed/production recovery drill; `production_verified=false`.
- [Managed Staging Restore Evidence #38126392496](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38126392496) passed only a minimal fixture-based restore smoke. It does not verify the managed destination against the full application schema; `application_schema_verified=false` and `production_verified=false`.
- The scheduled [Kaggle Ephemeral Worker Dispatcher #38126973473](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38126973473) was skipped and is not worker execution evidence.
- Passing standard CI, local runtime, and portable-package smoke tests do not prove a persistent production worker, real-media/live-provider processing, managed full-schema restore, OAuth/Drive, SMTP, Stripe, Sentry, performance/load, accessibility, legal/security acceptance, or penetration testing.
- Release status remains **PENDING — NOT PRODUCTION READY**. No paid worker/resource provisioning, quota-consuming inference, production-data mutation, or destructive live recovery drill is authorized without explicit owner approval.

> Owner: Project maintainers  
> Status rule: implementation, CI, ephemeral worker evidence, authenticated provider behavior, and production acceptance are separate levels.

## Current evidence update — 2026-10-12 UTC

Latest documentation/evidence commits:
- `1f00697f16a2fcde1cccb83e41750de6a2d092be` records the Groq smoke result and Windows restore fix in `docs/LOCAL_RUNTIME_FOLLOW_UP.md`.
- `9479e7a6bd056002b6ec9a937c2a1b8fe49656df` updates that follow-up with the final worker/gate results and corrects the earlier stale Windows restore-failure status.

Verified on restore-fix commit `644f4346f59d03b7185531e8621b26a989e502fb`:
- [Windows Local Runtime Evidence #38199416863](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416863) passed, including the dedicated SQLite restore regression on Windows Server 2025.
- [Windows Portable Package Evidence #38199416864](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416864) passed.
- [CI #38199416954](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416954), [Security #38199417025](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199417025), [CodeQL #38199416987](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416987), [Repository Gate #38199417001](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199417001), [Backup Restore Evidence #38199417034](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199417034), and [Real Worker Evidence #38199416934](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199416934) passed.
- [Groq free-tier provider smoke #38198919646](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38198919646) passed one synthetic request (HTTP 2xx). It is provider connectivity evidence only, not Burmese transcription-quality or production-provider acceptance.

The documentation-only follow-up commit `1f00697f16a2fcde1cccb83e41750de6a2d092be` also passed [CI #38199602836](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199602836), [Repository Gate #38199602788](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199602788), [CodeQL #38199602760](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199602760), and [Security #38199602710](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38199602710).

**Important scope limits:** ephemeral worker evidence is not a continuously running production worker. Synthetic fixtures are not real Burmese speech. Production Render provider flags remain disabled. The restore regression is now verified by the dedicated Windows test; this does not mean managed production disaster recovery has been proven.

Release status remains **PENDING — NOT PRODUCTION READY** until remaining real-media/provider, continuous worker, managed storage/restore, OAuth/Drive, SMTP, Stripe, Sentry, performance, accessibility, legal/compliance, and external security acceptance gates are addressed.

## Cloud-only continuation — 2026-10-12 (exact SHA `b1b2aa07c6608001bf78f97e45c0a10e07fbc7a9`)

- Corrected the webhook retry regression test so Celery eager mode recursively executes the autoretry wrapper; the prior run exposed a test-harness assertion issue, and the corrected test passed locally.
- Fresh checks on this exact SHA passed:
  - [CI #38211962880](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38211962880) — frontend typecheck/build, backend unit/security, PostgreSQL/Redis integration, and browser E2E.
  - [Security #38211962917](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38211962917).
  - [CodeQL #38211963015](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38211963015).
  - [Repository Gate #38211962839](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38211962839).
  - [Real Worker Evidence #38211962855](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38211962855) — ephemeral PostgreSQL 16/Redis 7, worker image, migrations, retry/DLQ/tenant integration, and synthetic-media worker smoke.
  - [Local Runtime Evidence #38211962889](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38211962889).
  - [Windows Local Runtime Evidence #38211962908](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38211962908).
  - [Windows Portable Package Evidence #38211962847](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38211962847).
- Additional isolated checks: SQLite Alembic upgrade/current reached `0018_tenant_backfill_guard`; backend unit/security selection passed (290 passed, 3 skipped, 83 deselected); frontend `npm ci`, `npm run typecheck`, and `npm run build` passed; Cloudflare Whisper Worker contract tests passed 2/2.
- OpenCode configuration audit: `opencode.json` parses as valid JSON; all four configured OpenRouter model IDs appeared in the public model catalogue at audit time, reported zero prompt/completion prices, and advertised tool support. This is catalogue metadata only: no inference was sent and it does not prove current quota, response quality, or a successful local OpenCode session.
- **Release remains PENDING — NOT PRODUCTION READY.** Synthetic worker smoke is not real Burmese speech acceptance or persistent production-worker proof. Managed database recovery, live provider integrations, user-media acceptance, legal/accessibility/security sign-off, and owner-gated actions remain open.

## Historical pre-PR #42/#43 main snapshot — 2026-10-10 UTC

- Current main SHA: `b75d074ab01b8f9e2ef4058dda03934eb91b3d8a` (PR #38 merge; PR #36 stale-worker recovery and PR #38 retry-exhaustion/DLQ idempotency coverage are included).
- PR #31 merged tenant-isolation negative cases for direct child-resource IDs. PR #32 merged storage lifecycle threshold/deletion-safety boundary tests (`a3ee23467ea2111e18b35523e698464d12c47024`). PR #33 merged a regression test proving asset metadata and audit history are preserved when storage-provider purge fails (`72154ae184f2316ee2c283be3184566edb91fe37`). PR #36 added stale real-processing job recovery tests; PR #38 added retry-exhaustion, failed-job/DLQ persistence, audit-event, and no-duplicate terminal-record coverage.
- PR-head checks for PR #32 and PR #33 passed, including backend, backend integration, E2E, CodeQL, Repository Gate, real-worker CI evidence, security scans, and local/Windows runtime/package smoke checks where present.
- Fresh checks on main merge SHA `b75d074ab01b8f9e2ef4058dda03934eb91b3d8a` passed: CI, Security, CodeQL, Repository Gate, Local Runtime Evidence, Real Worker Evidence, Windows Local Runtime Evidence, and Windows Portable Package Evidence.
- These changes improve automated regression coverage only. They do not establish live external-storage lifecycle/restore acceptance, a persistent production worker, authenticated real-audio Whisper inference, or full production end-to-end acceptance.
- Release status remains **PENDING — NOT PRODUCTION READY**. Do not run quota-consuming inference or provision billable worker capacity without explicit owner approval.

## Latest CI / evidence snapshot

### Latest implementation change — cross-tenant negative-case coverage

- PR #29 merged as `04bfedd5a79ee6eb90eaed83517c12c48282feb8`: added integration/security regression coverage that a second tenant cannot read/update another tenant's Series or Episode, read/retry its ProcessingJob, or list its assets/scripts/scenes/subtitles through a foreign Episode ID.
- All PR #29 checks passed on head `dc50efba0fcb91aacee8b352ded5fe12f25deb78`, including [CI/E2E](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621252), [Security scans](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621363), [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/runs/113942806678), [Real Worker Evidence](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621352), and [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37966621184).
- Fresh main-SHA checks on `04bfedd5a79ee6eb90eaed83517c12c48282feb8` are running and must be refreshed before release acceptance: [CI #1225](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303768), [Security #990](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303785), [CodeQL #597](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303746), [Repository Gate #249](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303857), [Real Worker Evidence #193](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303703), [Windows Local Runtime #32](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303910), and [Windows Portable Package #33](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303824). [Local Runtime #35](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37967303748) has already passed.
- This is stronger automated tenant-isolation evidence, not a substitute for a full resource-by-resource audit or production browser E2E. Gate G11 remains open until broader role/membership/cross-tenant negative cases are accepted in the target environment.


Main SHA: `4dd3d4f0b761858c83047263a310dfa5429ab48b` (PR #26 merged) passed fresh [CI #1217](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669315), [Security #982](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669353), [CodeQL #589](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669249), [Repository Gate #241](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669199), [Backup Restore #8](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669190), [Real Worker #191](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669286), [Local Runtime #33](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669461), [Windows Local Runtime #30](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669304), and [Windows Portable Package #31](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37965669256). These are automated CI/runtime checks, not production live-provider acceptance.

The parent SHA `b231e2d7c2cf5b2114edcf4d9ecd2a59e509f7f0` passed [CI](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092861), [Security](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092885), [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092877), and [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37961092923). [Real Worker Evidence #190](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37963422875) passed using isolated CI services and synthetic media. [Cloudflare Whisper Preflight #2](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37964550063) passed without inference. [Kaggle Dispatcher #12](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37962902195) passed configuration/database checks but did not launch because no due jobs were queued.

PR #26 is merged as `4dd3d4f`; SQLite restore now checks `PRAGMA integrity_check` before replacing a target. This does not prove a managed production restore.

## 1. Release status

**PENDING / not Production Ready.**

The live Render API is healthy and ready, and the Cloudflare Whisper Worker is deployed. The production release is still blocked by the absence of a continuously provisioned media worker and by external/live evidence gates.

## 2. VERIFIED

### Render API
**VERIFIED — 2026-10-08**

- Health: https://narrativ-forge.onrender.com/api/v1/health
- Readiness: https://narrativ-forge.onrender.com/api/v1/ready
- Live application SHA at checkpoint: `1369d9a3e4d8896cf6024fa45fa6810cc3cee890`
- Render service: https://dashboard.render.com/web/srv-davrqtu7bikc73f7isbg

Readiness returned database=`ok`, redis=`ok`.

### Cloudflare Whisper deployment
**VERIFIED — 2026-10-08**

- Worker: https://narrativ-forge-whisper.narrativ-forge.workers.dev
- Cloudflare account/deployment evidence confirms a 100% production version.
- `NARRATIV_SHARED_SECRET` binding exists.

**Scope:** deployment/reachability only. Authenticated real-audio transcription, VTT correctness, Subtitle Studio integration, quota/fallback behavior remain unverified.

## 3. WORKER BLOCKER

**BLOCKED — deployment capacity, not missing worker code.**

Repository worker implementation is present:

- Docker image: `apps/web-platform/backend/Dockerfile.worker`
- Entrypoint: `celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --beat` (configured concurrency defaults to 1 via `WORKER_MAX_CONCURRENCY`)
- Broker: Redis via `REDIS_URL`
- Durable job state: PostgreSQL
- Media tools: FFmpeg + OpenAI Whisper
- Worker task registration: `apps/web-platform/backend/app/workers/tasks.py`
- Failure recovery: late ACK, worker-lost rejection, retries, DLQ publication, stale-job recovery.

Current Render service evidence:
- service type = `web_service`
- plan = `free`
- instances = 1
- no background worker service exists in the connected Render workspace.

Render's current documentation says Free instances are available for web services, Postgres, and Key Value; private/background-worker compute plans start at paid tiers. citeturn0search1turn0search0

**Owner action:** provision a paid Render Background Worker or an equivalent external worker runtime. Do not convert the API web service into a fake worker.

Prepared configuration: `render.worker.yaml`.

## 4. RELEASE GATE MATRIX

| Gate | Status | Evidence / exact blocker |
|---|---|---|
| 1. Real media → FFmpeg → Whisper → DB/storage | BLOCKED | No continuously running worker. Worker code exists; live execution evidence cannot be produced until worker runtime exists. |
| 2. Retry / DLQ / duplicate-dispatch / failover | BLOCKED | Requires live worker/queue failure-injection drill. |
| 3. B2 / Supabase / Cloudinary lifecycle | PENDING | Provider routing exists, but no fresh live upload/download/delete/archive evidence for every configured provider. |
| 4. Whisper + fallback E2E | BLOCKED | Cloudflare Worker deployment is verified; authenticated real-audio E2E and fallback drill require worker/media execution. |
| 5. Google OAuth / Drive export / recovery | PENDING | Code defines `/api/v1/drive/google/start` and `/callback`; no authenticated production OAuth/export/recovery evidence. |
| 6. SMTP | PENDING | Render blueprint declares SMTP variables, but available Render tooling does not expose secret values. No real mailbox delivery evidence. |
| 7. Stripe | PENDING | Checkout/webhook code and Render variables exist; no live test-mode checkout/webhook evidence. |
| 8. Sentry | PENDING | Sentry initialization/code exists; DSN value and live event/alert evidence are not accessible through current tooling. |
| 9. Exact live Alembic head | VERIFY | Connected Render account has no Render-managed Postgres instance. Live `DATABASE_URL` points to an external provider, but current tooling cannot query that database or reveal the secret value. |
| 10. Backup / restore | PENDING | Backup/restore scripts exist; no real managed-Postgres restore drill has been completed. |
| 11. Production auth / cross-tenant E2E | PENDING | Playwright cross-tenant tests exist, but no fresh live production browser evidence. |
| 12. Full E2E / load / performance | BLOCKED | Full release E2E depends on worker/media path; no fresh representative load benchmark. |
| 13. Security / dependency / container scans | EXTERNAL ACTION | CI workflow exists for pip-audit, npm audit, CodeQL and Trivy, but no fresh scan artifacts tied to the release checkpoint are available. |
| 14. Accessibility / responsive / WCAG | EXTERNAL ACTION | No fresh automated + manual release audit artifact. |
| 15. Legal / privacy / compliance | EXTERNAL ACTION | Requires owner/legal sign-off; tooling cannot provide external approval. |
| 16. External penetration test | EXTERNAL ACTION | Requires independent tester/report/remediation evidence. |
| 17. Provider limits / terms / commercial use | EXTERNAL ACTION | Requires account-specific provider review; code defaults are not proof of current limits/terms/watermark/commercial rights. |

## 5. AUTOMATED EVIDENCE PREPARED

Previous automated gate execution reached the worker Docker build/migration stage but did not produce a passing VERIFIED result. Subsequent release-maturity commits have changed `main`, so no older run is treated as evidence for the current head. The GitHub connector available here exposes PR-associated workflow runs only; push-run completion is therefore not claimed from stale data.

Whisper fallback implementation was corrected against the deployed `narrativ-forge-whisper` Worker contract: signed Bearer token, episode binding, WAV input, and usage idempotency are now covered in code/tests. Live Burmese transcription quality remains unverified.

A CI evidence gate has been added on the worker branch/PR:

- Builds the real worker Docker image.
- Applies Alembic migrations against PostgreSQL.
- Runs retry/DLQ integration tests against PostgreSQL + Redis.
- Starts the real Celery worker.
- Generates deterministic media with FFmpeg.
- Runs the real Whisper CLI.
- Verifies processed video, transcript, DB completion, storage output, and current subtitle creation.

This does not replace production-provider/live evidence. The gate remains **execution pending** until its CI run produces a passing result.

## 6. PENDING

- Gates 3, 5, 6, 7, 8, 10, 11.
- Final UI/state audit and remaining Auto Production surfaces.

## 7. BLOCKED

- Gates 1, 2, 4, 12 are blocked directly or indirectly by the missing live worker.
- Gate 9 is blocked from verification by lack of access to the external production PostgreSQL instance.
- Production Ready is blocked until all applicable gates have fresh evidence.

## 8. EXTERNAL ACTION

- Gate 13: execute/attach release-SHA security scan artifacts.
- Gate 14: execute/attach automated + manual WCAG/responsive audit.
- Gate 15: obtain legal/privacy/compliance sign-off.
- Gate 16: obtain external penetration-test report and remediation evidence.
- Gate 17: perform account-specific provider terms/limits/commercial-use review.

## 9. NEXT

1. Owner provisions the worker using `render.worker.yaml` on a paid Render Background Worker or equivalent runtime.
2. Configure worker secrets/variables.
3. Run representative real-media E2E.
4. Run retry/DLQ/failover and Whisper fallback drills.
5. Execute remaining provider/recovery/security/accessibility/external gates.

## 10. Evidence rule

**Do not mark a gate VERIFIED from configuration, credentials, source code, unit tests, or a deployment manifest alone.**

Repository head and live deployment head must be tracked separately.

## 2026-10-08 continuation update

- Phase 15–36 continuation contracts/tests are present on `main`.
- Phase 37–45 operating-maturity contracts/tests are now present on `main` in `apps/web-platform/backend/app/services/operating_maturity.py` and `test_operating_maturity.py`.
- The latest known worker evidence attempt reached Docker image build and migrations, then failed during the integration test collection on an `orchestration.py` SyntaxError. The checked `main` source at the recorded SHA currently contains valid `ExecutionPlan.task_names` syntax; the failed attempt has been re-run and is currently in progress. Therefore the worker gate remains **NOT VERIFIED** until that rerun completes successfully.
- Local test execution from this environment was unavailable because outbound GitHub network resolution is blocked.
- Live credentials/provider/manual acceptance remain deferred as planned.
## 2026-10-08 execution continuation — A–D pass

- Phase 15–36 continuation tests were strengthened for deterministic export keys, NLE adjacency, and launch waiver handling.
- Phase 37–45 operating-maturity contracts remain implemented with unit coverage.
- Phase 46–51 were pre-staged in `PHASE_EXECUTION.md` for evidence ledger, provider acceptance matrix, production E2E rehearsal, billing reconciliation, release freeze, and post-launch watch.
- Worker evidence remains **NOT VERIFIED** until the rerun completes successfully. The last observed rerun was still `in_progress` at the time of this update.
- No production credentials were requested or fabricated; live-provider/manual gates remain deferred.


## 2026-10-08 Phase 46–51 implementation continuation

- **Phase 46:** persistent evidence ledger + database checks; VERIFIED requires commit SHA, workflow run, evidence reference, owner, and verification timestamp.
- **Phase 47:** persistent provider acceptance matrix; secrets remain outside the repository.
- **Phase 48:** release rehearsal/freeze/watch contracts and persistence store are implemented; live staging rehearsal still depends on the continuous worker runtime.
- **Phase 49:** persistent billing reconciliation with webhook-event and tenant/idempotency uniqueness.
- **Phase 50:** persistent release-candidate freeze record with migration/environment/rollback/evidence/checklist references.
- **Phase 51:** persistent post-launch watch events plus launch eligibility contract that refuses unfrozen or unsupported gates.
- Repository-level status workflow `.github/workflows/repository-gate.yml` now produces a single **Repository Gate** check on every `main` push/PR so the commit page can show green/red without opening Actions.
- Phases **52–60** are pre-staged in `PHASE_EXECUTION.md` and `ROADMAP.md` for trailer planning, Burmese translation, sound/BGM, thumbnails, LoRA/voice consistency, social analytics import, archive/PII purge, Manual Mode validation, and final UI/state audit.

**Current release status remains NOT Production Ready.** No live/provider/manual gate is promoted by these code-only changes.


## 2026-10-08 Phase 52–60 continuation

- Code-only contracts and tests now cover trailer planning, Burmese translation/subtitle normalization, BGM/audio rights and cueing, thumbnail shortlist selection, LoRA/voice consistency, social analytics idempotency, archive/PII purge protection, Manual Mode evidence, and UI/state/accessibility audit.
- Backend CI explicitly runs `unit or security` tests, while the PostgreSQL/Redis integration job remains separate; CodeQL runs Python and JavaScript/TypeScript analysis. Repository Gate aggregates the checks into one green/red status for the commit page.
- Phase 61–68 have been pre-staged in `PHASE_EXECUTION.md` and `ROADMAP.md`: performance/cost, worker autoscaling, provenance, enterprise audit, provider adapters, localization operations, monetization expansion, and post-launch SLO/error-budget operations.
- The new Phase 52–60 tests are marked `unit`, so they are included in the normal CI unit/security check. No separate live credential is required for these foundations.

**Evidence status:** code/test foundations are implemented; live worker, provider, billing, legal, accessibility and human acceptance gates remain unverified until fresh evidence exists.


## CI/test visibility hardening — 2026-10-08

- Backend CI now runs `unit or security` with `-vv`, so individual store/release/product regression tests are visible in the job log instead of being silently omitted by marker selection.
- Backend unit/security and PostgreSQL/Redis integration jobs each publish a JUnit XML artifact on every run.
- Previously unmarked backend regression suites were classified explicitly as `unit`, including content quality, magic links, production foundations/intelligence, provider quota/registry, resumable uploads, selective regeneration, and subtitle normalization.
- CodeQL remains a separate Python + JavaScript/TypeScript security check; Real Worker Evidence remains the real-media/Celery gate; Repository Gate aggregates all checks into the commit-level green/red surface.


## 2026-10-08 Phase 61–68 foundation continuation

Code-only contracts/tests are now staged for performance/cost budgets, worker autoscaling, provenance/lineage, enterprise audit, provider capability/circuit-breaker, localization QA, monetization ledgers, and SLO/error-budget operations. Live telemetry/providers/billing/enterprise acceptance remain unverified.


## Phase 61–68 code-foundation progress — 2026-10-08

Code-only foundations are now staged in `apps/web-platform/backend/app/services/phase_61_68.py` with unit coverage in `apps/web-platform/backend/tests/test_phase_61_68.py`: performance/cost budgets, worker autoscaling policy, provenance lineage, enterprise permissions, provider capability discovery, localization quality thresholds, billing metering validation, SLO budgets and incident/rollback policy. Live telemetry, billing, provider, enterprise and post-launch acceptance remain external gates.


## Phase 69–76 code-foundation progress — 2026-10-08

Code-only foundations are staged in `apps/web-platform/backend/app/services/phase_69_76.py` with unit coverage in `apps/web-platform/backend/tests/test_phase_69_76.py`: rollout/cohort policy, schema-drift detection, restore verification, privacy-request closure, secret/config readiness, dependency-license allowlisting, chaos-drill acceptance, and deterministic release evidence packs. These contracts do not claim live backup, privacy/legal, secret-manager, license, chaos or release acceptance.

### Phase 69–76 queue
69 progressive rollout/cohort control; 70 schema/data-quality drift; 71 restore verification; 72 privacy/data-subject operations; 73 secret/config readiness; 74 dependency/license governance; 75 chaos/recovery drills; 76 final release evidence pack.


## 2026-10-08 final code/evidence staging pass

- Phase 61–68 code-only foundations are implemented and unit-covered.
- Phase 69–76 code-only release-operations foundations are implemented and unit-covered.
- Phase 77–84 are pre-staged as the next queue: capacity/quota forecasting, API versioning, migration retirement, tenant portability, incident communications, support SLA, provider settlement seam, and final governance/evidence reconciliation.
- Latest main SHA: `dba5ea3eb781b1d3fa6fa3078faf3d4cd2b10999`.
- Fresh CI/CodeQL/Security/Repository Gate runs are active for the latest main changes; no green result is claimed until the run completes.


## 2026-10-08 Phase 77–84 code-only completion

- Phase 77–84 service contracts are implemented in `apps/web-platform/backend/app/services/phase_77_84.py`.
- Unit coverage is present in `apps/web-platform/backend/tests/test_phase_77_84.py` for quota forecasting, API sunset rules, migration retirement safety, deterministic tenant export keys, incident/SLA contracts, settlement math/idempotency, and final governance evidence completeness.
- The complete code-only phase queue through **84** is now staged/implemented on `main`.
- This does **not** mark production gates VERIFIED: live worker/runtime, provider, billing, backup/restore, privacy/legal, security, accessibility and human acceptance evidence remain external requirements.


## Final code-only queue checkpoint — 2026-10-08

- Phases **77–84 are implemented and unit-covered** on `main`.
- New service: `apps/web-platform/backend/app/services/phase_77_84.py`.
- New CI-visible unit suite: `apps/web-platform/backend/tests/test_phase_77_84.py` with `pytest.mark.unit`.
- Code-only backlog is exhausted through Phase 84. Remaining work is evidence/operations: live worker/runtime, real providers, billing, backup/restore, privacy/legal, security, accessibility, support/incident operations, and human acceptance.
- Latest main commit for this pass: `233d534f609b32ec86cfbab6af4fdd286a3d083d`.


## 2026-10-09 audit correction and architecture checkpoint

The previous entries above contain stale historical wording about the worker rerun being in progress. That is superseded by fresh GitHub evidence:

- Real Worker Evidence run #144: workflow run 37815224704, worker job 113444038377, conclusion success, head SHA 0edf3c4b222c144e74f2b9c9e06899cd30f5ac53.
- The successful smoke produced WORKER_SMOKE_OK with processed video, transcript, subtitle version, and duration evidence.
- Current main is 55d99dac9ab668a7f27bd944e6cfe3bacfcd5edd (README/status-badge change after the worker-evidence SHA).
- On current main, Repository Gate #145, CI #1121, Security #886, and CodeQL #493 all have successful completed runs tied to 55d99dac9ab668a7f27bd944e6cfe3bacfcd5edd.
- Therefore the worker implementation has fresh successful CI evidence, but that worker run was on the immediately preceding code SHA rather than the current README-only SHA. Do not overstate it as an exact-current-head worker run.

### Architecture audit result

A repository-wide cloud/local/package audit is now recorded in docs/CLOUD_LOCAL_PACKAGING_AUDIT.md.

The preferred implementation is incremental, not a rewrite:

1. preserve the existing Next.js/FastAPI/Celery/PostgreSQL/Redis/storage/FFmpeg/Whisper core;
2. add explicit local-runtime/package configuration;
3. add Windows-first package build/install/smoke verification;
4. add credentialed, opt-in cloud/provider E2E workflows using GitHub Secrets/Environments;
5. add reproducible backup/restore CI evidence;
6. keep all existing release gates 1–17 in force.

### Newly identified code prerequisite

Production tenant verification needs one hardening step before live E2E can be considered trustworthy: authenticated organization context currently resolves the user's first membership while the session also carries a user-global role. Multi-membership tenant context must become explicit and role resolution must be organization-scoped. The existing two-user cross-tenant test is useful but does not prove this multi-membership case.

### Current priority

Code work first: tenant-context/auth hardening, backup/restore verification harness, reusable credentialed verification workflow scaffolding, and package/runtime abstraction.

Evidence/manual work later: real provider credentials, live production acceptance, legal/compliance, accessibility/manual review, penetration testing, and account-specific provider terms/limits.

No paid Render worker is provisioned by this audit.


## 2026-10-09 cloud/local verification architecture progress

The repository is now being advanced toward reproducible `build -> run -> test -> evidence -> cleanup` verification rather than relying on permanent environments.

Completed in this increment:
- Authenticated sessions are now bound to an explicit organization membership when issued.
- Membership role is resolved from the selected organization, not the user's global role.
- Added `POST /api/v1/auth/switch-workspace` for explicit multi-membership workspace context.
- Added integration/security coverage proving a user with two memberships receives the selected organization's role and can switch context.
- Added `.github/workflows/backup-restore-evidence.yml` for an ephemeral PostgreSQL backup -> fresh database restore -> schema/data/Alembic integrity drill.
- Existing deterministic worker evidence remains separate from credentialed/live provider evidence.

Evidence status:
- Auth hardening: DONE at repository level; production authentication/cross-tenant behavior remains VERIFY until a fresh credentialed environment run.
- Backup/restore CI drill: IMPLEMENTED; remains VERIFY until the workflow completes successfully and uploads evidence.
- Production/provider gates are not promoted by these code changes alone.


## 2026-10-09 follow-up implementation checkpoint

- Fixed a compatibility defect found during source review: `issue_session()` now accepts the optional `organization_id` used by login, magic-link, and workspace-switch flows. Without this fix, those flows would raise a runtime argument error.
- Session verification now requires v1 tokens to use the legacy payload shape and v2 tokens to include an organization ID; mismatched version/payload shapes are rejected.
- Backup/restore evidence now includes a machine-readable JSON manifest with the exact commit SHA, workflow run/attempt, trigger, ephemeral database environment, check scope, timestamp, and an explicit `production_verified: false` marker.
- These changes are committed to `main`; this editing session has not executed GitHub Actions or run the backend test suite. The new backup/restore workflow and the auth integration test therefore remain **VERIFY**, not **VERIFIED**.

### Next implementation sequence

1. Confirm current-head CI and the backup/restore evidence workflow pass; fix any failures before adding more layers.
2. Add a shared verification entrypoint/evidence format for local runtime and package smoke tests.
3. Add explicit local-runtime configuration and a Windows package build/install/smoke workflow, keeping the desktop framework decision evidence-driven.
4. Add opt-in credentialed cloud/provider E2E with GitHub Environments, least-privilege secrets, redacted logs, and guaranteed cleanup.
5. Complete live gates separately: continuous worker, provider lifecycle, auth/cross-tenant, backup/restore, billing/email/Drive/Sentry, security, accessibility, legal, and penetration testing.


## Local runtime verification increment (2026-10-09)

- Added `.github/workflows/local-runtime-evidence.yml` for a fresh SQLite/local-storage API smoke: migrate, start FastAPI, check health/readiness, verify DB and local storage, upload logs and JSON evidence, and stop the API during cleanup.
- Added `docs/LOCAL_RUNTIME.md` describing what the current local API gate proves and what remains required for a Windows package and offline media worker.
- This workflow has not yet been confirmed green in GitHub Actions. Status: IMPLEMENTED / VERIFY. It does not prove a Windows installer or production providers.

Next: inspect the local-runtime and backup/restore workflow runs; add deterministic local worker/media smoke; prototype Windows sidecar lifecycle; then build and test install/launch/E2E/cleanup. Credentialed cloud E2E and production acceptance remain separate gates.


- Added `.github/workflows/windows-local-runtime-evidence.yml` to check FastAPI + SQLite + local filesystem behavior on a clean Windows runner, with API process cleanup and evidence artifact collection. This is a compatibility smoke, not an installer/package test. Execution remains VERIFY until the workflow run and artifact are inspected.


## 2026-10-09 local runtime evidence results and backup gate corrections

- **Ubuntu local runtime smoke: VERIFIED for the narrow API gate.** Run: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37883066599/job/113667129807. Fresh SQLite migrations, API health/readiness, database connectivity, and local filesystem write/read passed. This does not prove package installation or media-worker/offline processing.
- **Windows local API smoke: VERIFIED for the narrow API gate.** Run: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37883392980/job/113667914332. Windows dependency installation (excluding PyICU/myanmartools), migrations, API health/readiness, SQLite connectivity, local filesystem write/read, and cleanup passed. ICU-dependent Burmese normalization and packaged media processing remain untested.
- The first Windows attempt exposed that stock Windows runners cannot compile PyICU without an ICU/pkg-config toolchain. The smoke now explicitly excludes PyICU and myanmartools rather than disguising that gap; a future Windows media/package gate must solve and verify these dependencies.
- The backup/restore workflow exposed two real issues and has been corrected: deterministic seed rows now include required timestamps, and the migration assertion now uses the actual current Alembic head `0017_release_maturity` (not the stale `0017_asset_deleted_at` value).
- The latest backup/restore run is still in progress while installing its narrowed migration-only dependency set. Do not mark backup/restore VERIFIED until that run succeeds and its evidence artifact is inspected.
- The current Windows API smoke does not install a desktop package and is not evidence of a finished Windows installer.

### Remaining implementation order

1. Finish and inspect the current PostgreSQL backup -> fresh restore run; fix any remaining failure and rerun until green.
2. Confirm the current-head Repository Gate / CI / Security / CodeQL checks settle successfully; rerun the required gates if a stale commit's run was cancelled by a newer push.
3. Add a deterministic local worker/media test, including explicit FFmpeg/Whisper availability and honest skip reasons.
4. Prototype Windows sidecar lifecycle, then select a desktop shell only after a repeatable artifact build works.
5. Add install -> launch -> API/UI E2E -> evidence -> shutdown/cleanup on a clean Windows runner.
6. Add opt-in, credentialed cloud/provider E2E and live production acceptance as separate gates.


## Verification results update (2026-10-09)

- **PostgreSQL backup/restore CI: VERIFIED for the ephemeral PostgreSQL 16 drill.** Run: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37883550172/job/113668073504. Migration to head, required marker seed, custom-format backup, restore into a fresh database, Alembic-head check, and marker-row integrity all passed. Evidence artifact: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37883550172/artifacts/11594979796. This is not a live managed-production restore.
- **Ubuntu local API + SQLite smoke: VERIFIED for its defined scope.** Run: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37883066599/job/113667129807.
- **Windows local API + SQLite smoke: VERIFIED for its defined scope.** Run: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37883392980/job/113667914332. ICU-dependent Burmese processing and package installation are explicitly outside this smoke.
- Updated Repository Gate so a commit superseded by a newer `main` commit exits without misreporting expected concurrency cancellations as a current-head failure. The new gate logic itself still needs a fresh run to verify.
- Auth/tenant integration changes remain VERIFY because their full integration/security suite has not yet been confirmed green on the latest main SHA.


## 2026-10-09 verified auth, worker, and Windows portable bundle checkpoint

- **Base main SHA for this checkpoint:** 5ca18fedae2277f8e3a9137c3fb69f2d467a00d3.
- **CI: VERIFIED for this SHA.** Backend unit/security, PostgreSQL backend integration, frontend typecheck/build, and Playwright E2E all passed: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37888111841.
- **Security: VERIFIED for this SHA.** SAST, dependency audit, and container scan passed: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37888111873.
- **CodeQL: VERIFIED for this SHA.** https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37888112026.
- **Repository Gate: VERIFIED for this SHA.** https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37888111887.
- **Real worker evidence: VERIFIED on the parent code SHA 92e0b36bd026201999f3ef791fa7ed1c2537ae06.** The worker image built, the retry/DLQ/tenant integration suite passed, the Whisper tiny model cache was prepared, a real Celery worker processed generated media through FFmpeg/Whisper, output/transcript/subtitle integrity passed, and worker cleanup passed: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37886970008. The package/docs-only merge did not change backend or worker code.
- **Windows portable API/UI package: VERIFIED for its explicitly limited scope on this SHA.** The workflow built a Next.js standalone frontend, assembled a ZIP, extracted that exact ZIP into a clean Windows directory, installed the API dependencies, applied SQLite migrations, started API + UI, checked health/readiness/login, stopped processes, and uploaded a checksum/evidence artifact: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37888111933. Evidence artifact: https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37888111933/artifacts/11596658431.
- **Local runtime evidence: VERIFIED for this SHA.** https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37888111994.
- The package is a **portable API/UI bundle**, not a standalone installer or offline desktop application. It requires Python 3.12, Node.js 20, and internet access for first-run dependency installation. It does not include the Celery worker, Redis, FFmpeg/Whisper model, PyICU, or myanmartools; Burmese processing, offline media processing, installer/uninstaller, code signing, and production-provider E2E remain NOT VERIFIED.
- Ephemeral PostgreSQL backup/restore was verified previously, but no live managed-production restore or credentialed provider E2E is claimed. Production readiness remains gated on provider secrets/environments and external acceptance work.


## 2026-10-09 current-head verification checkpoint — `b67d4620038cb9207180a737815fc0a1213ee6ca`

This section supersedes earlier historical statements about pending CI runs or the older repository head. Earlier dated entries are retained as history; use this checkpoint for the current state.

### Verified at current main SHA

- GitHub [CI](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515865): success.
- GitHub [Security](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515817): success.
- GitHub [CodeQL](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515813): success.
- GitHub [Repository Gate](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37889515819): success.
- Render deployment `dep-db47rg0ae00c739pgs90` is live at this repository SHA. This confirms deploy state, not a fresh HTTP health/readiness probe.
- The Windows portable package persistence gate succeeded on the immediately preceding main SHA `ee448cb82ccd4b68235c9264ac474019c961a994`. Scope remains API/UI start-stop-restart and local marker persistence; no packaged worker/media runtime.

### Newly merged workflow and operational documentation

- `.github/workflows/cloudflare-whisper-live-evidence.yml` provides a manual-only, explicit-confirmation authenticated request against the deployed Cloudflare Whisper Worker. It has **not been run** as of this checkpoint; no live inference success is claimed.
- `docs/DEPLOYMENT.md` describes the current deployment checkpoint and the opt-in live test.
- `docs/OWNER_ACTION_CHECKLIST.md` is the ordered owner runbook for adding GitHub environment secrets, running live Whisper acceptance, provisioning the optional paid worker, and closing remaining release gates.
- `.github/workflows/worker-evidence.yml` is being improved to upload a redacted manifest and worker/smoke logs with a 14-day retention window. Its result must be confirmed by the PR workflow run before this evidence-collection change is treated as verified.

### Remaining blockers / owner actions

1. Run Cloudflare Whisper live evidence only after setting `CLOUDFLARE_WHISPER_WORKER_URL` and `CLOUDFLARE_WHISPER_SHARED_SECRET` as protected `production` environment secrets and explicitly approving the quota-consuming inference.
2. Decide whether to approve paid compute for a continuous Render Background Worker. The separate `render.worker.yaml` is a reference blueprint and is not provisioned. Without that service, production asynchronous media processing and live retry/DLQ/failover remain blocked.
3. Run/inspect fresh backup/restore evidence for the intended release SHA; the existing PostgreSQL 16 test is ephemeral CI evidence, not a production managed-database restore.
4. Keep the Windows package marked prototype until worker/media dependencies, ICU-dependent Burmese processing, installer lifecycle, upgrades, backup/restore, and full media E2E are covered.
5. Complete live provider lifecycle, production tenant E2E, OAuth/Drive, SMTP, Stripe, Sentry, security/container scans, performance, accessibility, legal/privacy, and external penetration testing with exact evidence.

**Release status remains NOT Production Ready.** Configuration, source tests, a live API deployment, and synthetic CI fixtures do not independently verify production media processing or external-provider behavior.


## 2026-10-09 Cloudflare Whisper live acceptance failure

- Live evidence run [#37895020420](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37895020420) failed before authenticated inference. The unauthenticated POST returned HTTP 403; the expected Worker contract is HTTP 401. The signed-token request was not reached, so this run does not establish whether the configured shared secret matches.
- Cloudflare API metadata confirms the Worker has the `NARRATIV_SHARED_SECRET` secret binding, but the secret value is not retrievable from the binding listing. Do not claim the value is known.
- The related workflows are being hardened on PR #22: validate the exact workers.dev hostname and secret length; send the configured allowed Origin; do not follow redirects; record safe error/status codes without saving response bodies; make Worker deployment manual-only, require an explicit confirmation that Render's secret is already synchronized, and use the protected production environment for secret synchronization.
- The exact same shared secret must be configured in GitHub `production/CLOUDFLARE_WHISPER_SHARED_SECRET`, Cloudflare Worker `NARRATIV_SHARED_SECRET`, and Render API `CLOUDFLARE_WHISPER_SHARED_SECRET`. If the old value is lost, rotate all three together before testing.
- **Whisper authenticated E2E remains NOT VERIFIED.** Do not run another quota-consuming inference until the coordinated secret setup and manual Worker deployment are complete and the owner approves the test.


## 2026-10-09 latest Cloudflare Whisper 403 investigation

- Latest live-evidence job: [run #37907157973, job 113743278697](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37907157973/job/113743278697), commit `adeb425185f163775f03b779553a8e148284f363`.
- Failure point: the unauthenticated POST received HTTP 403 rather than the Worker contract's HTTP 401. The redacted artifact reports `Content-Type: text/plain`, a Cloudflare `CF-Ray`, and no recognized Worker JSON error. The authenticated request did not run; inference success is false.
- Read-only Cloudflare API metadata showed the `narrativ-forge-whisper` script exists, workers.dev is enabled, and `ALLOWED_ORIGIN` is configured as the same Netlify origin as repository `wrangler.jsonc`. Latest deployment metadata was dashboard-sourced on 2026-10-09. This does not establish the exact public response path or the secret value.
- Diagnosis: the observed response is consistent with an edge/access-layer rejection or a public hostname/deployed handler mismatch. It does **not** prove a shared-secret mismatch. Do not rotate secrets or rerun billable inference based on this result alone.
- Added `.github/workflows/cloudflare-whisper-preflight.yml`: GET-only, unauthenticated, no audio and no Workers AI call. Expected result is the Worker JSON 405 method guard. It records only safe response metadata and a short sanitized preview.
- Hardened live-evidence diagnostics to record CF-Ray, content type, server, body hash, and sanitized preview; non-JSON Cloudflare 403 now produces an explicit edge/deployment diagnosis.
- Hardened the manual Worker deploy workflow with a GET-only post-deploy smoke check. It still requires explicit owner confirmation that Render's API secret is already synchronized.
- Updated `docs/OWNER_ACTION_CHECKLIST.md`, `docs/DEPLOYMENT.md`, and `docs/TROUBLESHOOTING.md` with the latest evidence and ordered recovery path.
- **Still blocked:** public Worker handler preflight has not yet passed. Do not run authenticated inference until preflight passes and the owner explicitly approves possible Workers AI quota use. Production readiness remains NOT VERIFIED.


## Latest security hardening checkpoint — 2026-10-12 UTC

Current application-code checkpoint: `b374df9e1e455e35eaa9847d78fb7c9af70f2393` — “Harden outbound webhook destination validation”.

Verified on this exact commit:
- [CI #38201576482](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576482) — passed.
- [Security #38201576514](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576514) — passed.
- [CodeQL #38201576494](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576494) — passed.
- [Repository Gate #38201576503](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576503) — passed.
- [Real Worker Evidence #38201576538](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576538) — passed; this remains ephemeral CI worker evidence, not continuous production operation.
- [Windows Portable Package Evidence #38201576528](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576528) — passed.
- [Windows Local Runtime Evidence #38201576459](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576459) and [Local Runtime Evidence #38201576477](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576477) — passed.

Changes included on this checkpoint and its direct parent:
- Cloudflare Whisper inference failures now return a generic error instead of exposing provider exception text; Worker contract tests cover diagnostic redaction and invalid-token rejection before inference.
- Outbound webhook destination validation rejects malformed ports, embedded URL credentials, DNS failures/empty results, and any resolved non-global address; regression coverage includes loopback and mixed public/private DNS answers.
- **Scope limit:** destination validation resolves and checks addresses before the HTTP client makes its request; it is not IP pinning and should not be described as complete DNS-rebinding prevention.

Release status remains **PENDING — NOT PRODUCTION READY**. Passing CI does not establish real Burmese speech quality, continuous worker availability, managed production restore, or external-provider acceptance. Keep production provider flags disabled and remain free-first unless the owner explicitly approves changes.

## 2026-10-12 Burmese media sample preflight

- A 58.7-second chat-uploaded MP4 was inspected without adding the media to Git. FFprobe/FFmpeg read the H.264 portrait video and AAC audio; conversion to 16 kHz mono PCM succeeded.
- Technical findings: 576 × 1024 at 30 fps; AAC-LC 44.1 kHz stereo; no embedded subtitle stream detected; approximately 2.815 seconds of terminal silence detected at a -45 dB threshold; mean audio level -17.3 dBFS and peak approximately 0.0 dBFS. Review the end silence and listen for audible clipping/distortion.
- Evidence: [Burmese sample technical preflight report](docs/Report/BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md) and [acceptance checklist](docs/BURMESE_MEDIA_ACCEPTANCE.md).
- **Burmese speech-quality acceptance — FAILED for current Whisper candidates; overall acceptance remains PENDING.** The canonical local worker completed on the supplied sample, but its historical transcript reports `language: my` because the worker used to force `--language my`; its text contains 252 CJK ideographs and no Myanmar-script characters. Separate `tiny` auto-detection and checksum-verified `large-v3-turbo` CPU inference both detected Chinese. The turbo candidate had 3 segments, 41 non-whitespace characters, 0 Myanmar-script characters, and 24 CJK ideographs. `small` auto-detection completed with 5 segments and 152 characters, detected `my`, but had no Myanmar-script characters; forced-`my` `small` output had only 6 characters across 4 segments and no Myanmar-script characters. No Burmese-speaking human/reference review was performed, and auto-detected Chinese does not prove the spoken language. A current uncommitted code change now preserves detected language instead of forcing `my`; its focused tests passed, but the canonical worker has not yet been rerun after this change. The input and transcript candidates remain outside Git. Do not approve any candidate as Burmese. See [technical preflight report](docs/Report/BURMESE_SAMPLE_PREFLIGHT_2026-10-12.md) and [acceptance checklist](docs/BURMESE_MEDIA_ACCEPTANCE.md).
- **Still pending:** privately confirm the spoken language; if the clip is Burmese, obtain an owner-approved reference or Burmese-speaking review and continue ASR diagnosis. Also assess subtitle timing/readability and rendered playback, and record the exact source commit for any new canonical worker evidence. No authenticated cloud inference or production change was made.
- **Windows subprocess regression — PASS on the inspected dirty worktree:** subprocess text decoding explicitly uses UTF-8 with `backslashreplace`; the focused test file passed 6 tests with 2 skips after its Windows process-tree startup test window was increased from 0.2 to 2 seconds. Production timeout behavior was not changed. Base HEAD was `95aa9163cc40383a8c44c3a5f445e4de899116e4`; the tested edits are uncommitted and have no exact commit SHA.
- No authenticated cloud inference, paid resource provisioning, production-data mutation, or destructive recovery was performed. Release status remains **PENDING — NOT PRODUCTION READY**.

## Cloud-only continuation — exact SHA `07fd3ac3bb39ee5d4b41b4bd90960e169ffd6202` (2026-10-12 UTC)

- Hardened release maturity: release launch eligibility now requires all release artifact references (version, migration plan, environment manifest, rollback plan, evidence ledger, and acceptance checklist) rather than accepting an incomplete release package.
- Hardened AI adapter endpoint validation: unknown provider families now fail closed instead of allowing arbitrary compatible-base URLs. Added regression coverage for rejecting unknown providers before any HTTP request.
- Focused local regression tests passed: 38 passed. Backend unit/security selection passed: 297 passed, 3 skipped. `git diff --check` passed before the GitHub commits.
- All fresh exact-SHA GitHub Actions checks passed on `07fd3ac3bb39ee5d4b41b4bd90960e169ffd6202`:
  - [CI #38220724248](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38220724248) — backend unit/security, PostgreSQL/Redis integration, frontend typecheck/build, browser E2E, and Cloudflare Whisper Worker contract tests.
  - [Security #38220724268](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38220724268) — dependency audit, SAST, and container scan.
  - [CodeQL #38220724133](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38220724133) — JavaScript/TypeScript and Python analysis.
  - [Repository Gate #38220724300](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38220724300).
  - [Real Worker Evidence #38220724354](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38220724354) — ephemeral worker integration with synthetic media.
  - [Windows Local Runtime Evidence #38220724290](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38220724290).
  - [Windows Portable Package Evidence #38220724344](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38220724344).
- These checks are automated/ephemeral evidence only. They do not prove persistent production worker capacity, authenticated Burmese real-audio inference, production provider configuration, managed production restore, or owner/legal/security acceptance.
- Release status remains **PENDING — NOT PRODUCTION READY**. No paid resources were provisioned, no production data was changed, and no quota-consuming inference was run.

## Cloud-only continuation — Worker request-size hardening and live endpoint checks (2026-10-12 UTC)

Code SHA checked: `6c53f953747d7ec3c18cf4872b85b96164c897b7`.

- Hardened `apps/web-platform/cloudflare/whisper-worker/src/index.ts`: reject oversized declared `Content-Length` before reading the request, and enforce the 50 MiB cap while streaming the body so chunked requests cannot bypass the limit by forcing an unbounded `arrayBuffer()` allocation. Added regression tests for declared and chunked oversized bodies.
- Cloudflare Whisper Worker contract tests: **4 passed** locally. Wrangler `deploy --dry-run` completed successfully (5.30 KiB upload / 1.90 KiB gzip); this was a bundle validation only, not a deployment. `git diff --check` passed.
- Fresh live, non-billable checks: Cloudflare Whisper GET-only probe returned HTTP 405 JSON `Method not allowed` with a Cloudflare Ray ID, confirming the Worker handler is reached. No audio, token, or Workers AI inference was sent. Render `/api/v1/health` returned HTTP 200; `/api/v1/ready` returned HTTP 200 with database and Redis both `ok`.
- Read-only Cloudflare API audit: `narrativ-forge-whisper` has a 100% traffic deployment and the `NARRATIV_SHARED_SECRET` binding is present; `ALLOWED_ORIGIN` matches the configured Netlify HTTPS origin. The new request-size hardening has **not** been deployed to the live Worker. Deployment remains manual-only and requires explicit confirmation that the Render API shared secret matches the protected GitHub production secret.
- Read-only Netlify audit: current production deploy is `ready` but references older commit `777fba6ca92ce59e53e741b976bc9ea9692b45c1` (2026-10-06), not the current main code. Site access is configured to require team SSO. Treat frontend redeployment and any access-policy change as owner-approved production actions; neither was performed.
- All exact-SHA GitHub checks passed on `6c53f953747d7ec3c18cf4872b85b96164c897b7`: [CI #38225593771](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38225593771), [Security #38225593824](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38225593824), [CodeQL #38225593759](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38225593759), and [Repository Gate #38225593748](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38225593748). CI includes backend unit/security tests, PostgreSQL/Redis integration, frontend typecheck/build, browser E2E, and Cloudflare Worker contract tests.
- Release remains **PENDING — NOT PRODUCTION READY**. A continuously running media worker still requires owner approval for billable capacity; Burmese real-speech acceptance, managed backup/restore, live provider integrations, and legal/accessibility/security sign-off remain open. No paid resources, production data changes, destructive recovery, or quota-consuming inference were used.

## Cloud deployment follow-up — verified after Worker deploy #12 (2026-10-12 UTC)

This section supersedes the older statement above that the request-size hardening had not yet been deployed. It was deployed afterward by the manual Worker workflow.

- **GitHub Worker deploy:** [run #38260359375](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38260359375) completed successfully on main SHA `95aa9163cc40383a8c44c3a5f445e4de899116e4`. All eight substantive job steps succeeded, including source deployment, secret-binding configuration, and GET-only handler verification without AI inference.
- **Cloudflare read-only API confirmation:** Worker `narrativ-forge-whisper` has a current 100%-traffic version `304d7bbf-66a3-4d5a-b9ee-8615b7c1cc9c`, deployment created at `2026-10-12T14:05:52Z`. The `AI`, `ALLOWED_ORIGIN`, and `NARRATIV_SHARED_SECRET` bindings are present. Secret values were not read or printed.
- The deployed source includes the request-body size guard added on parent SHA `6c53f953747d7ec3c18cf4872b85b96164c897b7`: declared `Content-Length` rejection and bounded streaming enforcement of the 50 MiB cap. Workflow evidence verifies the handler/method guard, not transcription quality.
- **Render API:** Render reports the service is not suspended, plan `free`, and latest deployment `dep-db69upmk1f9s73f3ve0g` is live on the same SHA `95aa9163cc40383a8c44c3a5f445e4de899116e4`. The latest logs show application startup completed, Uvicorn running, and `GET /` returned HTTP 200. Render auto-deploy on commits to `main` is enabled; documentation updates should be reviewed through a branch/PR rather than committed directly to main to avoid triggering an unnecessary Render build.
- The combined-status connector returned no status objects for this SHA, so this note does not claim fresh green CI checks for `95aa9163`; use the linked workflow run for Worker deployment evidence and the individual Actions runs for other gates.
- **Still blocked:** continuous media-worker capacity, authenticated real-audio/Burmese transcription acceptance, production provider/fallback behavior, managed production backup/restore, external integration acceptance, performance/accessibility/legal/security sign-off. No paid resource was created and no quota-consuming inference was run.
- **Release remains PENDING — NOT PRODUCTION READY.**


- **Netlify rechecked after this note was drafted:** the currently published production deploy is `6ac4f8aba9c7aa00082031dc`, state `ready`, but it still points to old main commit `777fba6ca92ce59e53e741b976bc9ea9692b45c1` from 2026-10-06, not current main SHA `95aa9163cc40383a8c44c3a5f445e4de899116e4`. Netlify project access currently requires team SSO for all projects. Neither deploy nor access settings were changed. See [published deploy](https://app.netlify.com/projects/harmonious-nasturtium-53a1d6) and [source commit](https://github.com/dragonknighttw-cmd/Narrativ-Forge/commit/777fba6ca92ce59e53e741b976bc9ea9692b45c1).


## 2026-10-14 exact-SHA plan-PR verification (PR #75)

- Documentation-only PR head: `97030d17b5f0d2fd8c121a9b5b590dc1d19df70b`. No application code was changed in this plan-reconciliation PR.
- Exact-SHA workflows: [Repository Gate #38503795475](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38503795475) **passed**; [Security #38503795675](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38503795675) **passed**; [CodeQL #38503795460](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38503795460) **passed**; [CI #38503795609](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38503795609) **failed**.
- CI confirms the approval route defect: backend integration suite **4 failed, 68 passed, 1 skipped**. All four failures report `NameError: name 'approved_at' is not defined` from `apps/web-platform/backend/app/api/routes/review.py`. The Playwright production flow also fails at the approval request; the other two E2E tests passed. This is now tracked as [Issue #76](https://github.com/dragonknighttw-cmd/Narrativ-Forge/issues/76).
- Frontend typecheck/build, backend unit/security job, and Cloudflare Worker contract job passed in the same CI run; this does not offset the failed integration/E2E gates.
- Do not merge this documentation PR as release approval and do not deploy production. Release remains **PENDING — NOT PRODUCTION READY**. Next code task is the separate fix for Issue #76, followed by exact-SHA backend integration + E2E reruns.


## 2026-10-14 follow-up — approval bug fix candidate PR #77

- Fix candidate PR: [#77](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/77), branch `fix/review-approval-timestamp`, exact SHA `a05a97752a30889d691c687ea47b519a089e7e6b`. The route now defines one UTC approval timestamp and reuses it for `ReviewRecord.reviewed_at` and the response; an integration test asserts episode ID, approved status, and a non-empty `approved_at` response field.
- Exact-SHA CI [#38561471370](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38561471370) **passed**: backend unit/security **303 passed, 3 skipped**; PostgreSQL/Redis integration **72 passed, 1 skipped**; frontend build/typecheck passed; browser E2E passed; Cloudflare Worker contract tests passed.
- Security [#38561471555](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38561471555), CodeQL [#38561471545](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38561471545), Repository Gate [#38561471367](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38561471367), Local Runtime Evidence [#38561471447](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38561471447), Windows Local Runtime Evidence [#38561471702](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38561471702), and Windows Portable Package Evidence [#38561471509](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38561471509) **passed**.
- Real Worker Evidence [#38561471401](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38561471401) is still running; do not call all gates complete until it finishes.
- Fix remains in an open PR and has not been merged. No production deployment or cloud inference was performed. Burmese real-speech quality remains unaccepted; release remains **PENDING — NOT PRODUCTION READY**.


## 2026-10-14 final follow-up — approval fix merged

- Approval bug fix [PR #77](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/77) was merged as [`6dbd4fabe715c06b565c6e53cf187b7373bbb9df`](https://github.com/dragonknighttw-cmd/Narrativ-Forge/commit/6dbd4fabe715c06b565c6e53cf187b7373bbb9df). Confirmed the default-branch `review.py` blob contains the fix.
- All exact-SHA workflows on tested candidate `a05a97752a30889d691c687ea47b519a089e7e6b` completed successfully: CI (303 backend unit/security passed, 3 skipped; 72 PostgreSQL/Redis integration passed, 1 skipped; frontend, E2E, Worker contract passed), Security, CodeQL, Repository Gate, Local Runtime Evidence, Windows Local Runtime Evidence, Windows Portable Package Evidence, and Real Worker Evidence.
- Issue [#76](https://github.com/dragonknighttw-cmd/Narrativ-Forge/issues/76) is closed as completed. No production deployment or cloud inference was performed.
- These checks validate the fix candidate, not the whole product's release readiness. Burmese real-speech quality acceptance, external provider integration, managed backup/restore, and owner/legal/accessibility/security sign-off remain open. Release remains **PENDING — NOT PRODUCTION READY**.


## Cloudflare follow-up — 2026-10-15

- Whisper's `ALLOWED_ORIGIN` points to a Netlify site that has not been confirmed as the canonical frontend; Render also has a named frontend service. Resolve frontend ownership/origin before changing CORS. Secret values were not read.
- Whisper has a `NARRATIV_SHARED_SECRET` binding; edge Worker returned no secret bindings. Both Workers have Logpush disabled. Current live HTTP smoke tests were not verified through the available inspection path.
- See [Infrastructure Audit](INFRASTRUCTURE_AUDIT.md) and [Deployment](docs/DEPLOYMENT.md).
