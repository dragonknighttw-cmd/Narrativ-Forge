# Narrativ Forge — Current State

> Owner: Project maintainers
> Last Updated: 2026-10-09
> Status evidence is environment-specific. Code/config alone never promotes a gate to VERIFIED.

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

- Docker image: `web-platform/backend/Dockerfile.worker`
- Entrypoint: `celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --beat` (configured concurrency defaults to 1 via `WORKER_MAX_CONCURRENCY`)
- Broker: Redis via `REDIS_URL`
- Durable job state: PostgreSQL
- Media tools: FFmpeg + OpenAI Whisper
- Worker task registration: `web-platform/backend/app/workers/tasks.py`
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
- Phase 37–45 operating-maturity contracts/tests are now present on `main` in `web-platform/backend/app/services/operating_maturity.py` and `test_operating_maturity.py`.
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

Code-only foundations are now staged in `web-platform/backend/app/services/phase_61_68.py` with unit coverage in `tests/test_phase_61_68.py`: performance/cost budgets, worker autoscaling policy, provenance lineage, enterprise permissions, provider capability discovery, localization quality thresholds, billing metering validation, SLO budgets and incident/rollback policy. Live telemetry, billing, provider, enterprise and post-launch acceptance remain external gates.


## Phase 69–76 code-foundation progress — 2026-10-08

Code-only foundations are staged in `web-platform/backend/app/services/phase_69_76.py` with unit coverage in `tests/test_phase_69_76.py`: rollout/cohort policy, schema-drift detection, restore verification, privacy-request closure, secret/config readiness, dependency-license allowlisting, chaos-drill acceptance, and deterministic release evidence packs. These contracts do not claim live backup, privacy/legal, secret-manager, license, chaos or release acceptance.

### Phase 69–76 queue
69 progressive rollout/cohort control; 70 schema/data-quality drift; 71 restore verification; 72 privacy/data-subject operations; 73 secret/config readiness; 74 dependency/license governance; 75 chaos/recovery drills; 76 final release evidence pack.


## 2026-10-08 final code/evidence staging pass

- Phase 61–68 code-only foundations are implemented and unit-covered.
- Phase 69–76 code-only release-operations foundations are implemented and unit-covered.
- Phase 77–84 are pre-staged as the next queue: capacity/quota forecasting, API versioning, migration retirement, tenant portability, incident communications, support SLA, provider settlement seam, and final governance/evidence reconciliation.
- Latest main SHA: `dba5ea3eb781b1d3fa6fa3078faf3d4cd2b10999`.
- Fresh CI/CodeQL/Security/Repository Gate runs are active for the latest main changes; no green result is claimed until the run completes.


## 2026-10-08 Phase 77–84 code-only completion

- Phase 77–84 service contracts are implemented in `web-platform/backend/app/services/phase_77_84.py`.
- Unit coverage is present in `web-platform/backend/tests/test_phase_77_84.py` for quota forecasting, API sunset rules, migration retirement safety, deterministic tenant export keys, incident/SLA contracts, settlement math/idempotency, and final governance evidence completeness.
- The complete code-only phase queue through **84** is now staged/implemented on `main`.
- This does **not** mark production gates VERIFIED: live worker/runtime, provider, billing, backup/restore, privacy/legal, security, accessibility and human acceptance evidence remain external requirements.


## Final code-only queue checkpoint — 2026-10-08

- Phases **77–84 are implemented and unit-covered** on `main`.
- New service: `web-platform/backend/app/services/phase_77_84.py`.
- New CI-visible unit suite: `web-platform/backend/tests/test_phase_77_84.py` with `pytest.mark.unit`.
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

- **Current main SHA:** 5ca18fedae2277f8e3a9137c3fb69f2d467a00d3.
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
