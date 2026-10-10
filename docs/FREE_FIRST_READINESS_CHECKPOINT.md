# Free-first production-readiness checkpoint

**Checkpoint date:** 2026-10-11 UTC  
**Main SHA at this checkpoint:** e672bf0c5f75441e0bd9556db6811320a33a7a5e  
**Release status:** PENDING — NOT PRODUCTION READY  
**Policy:** Do not run Cloudflare Whisper live inference, consume provider quota, or provision potentially billable resources without explicit owner approval.

## Latest implementation checkpoint

- PR #49 merged: reserves Whisper audio usage before remote inference so ambiguous provider outcomes are accounted for.
- PR #50 merged: Redis dispatch locks are released only by the matching dispatch token.
- PR #51 merged: roll back the SQLAlchemy transaction before entering local Whisper fallback.
- PR #52 merged: Kaggle scheduled launches require repository Actions variable ENABLE_KAGGLE_DISPATCH=true; manual dispatch requires explicit confirm_kaggle_dispatch=true.
- PR #53 merged: concurrent requests that bootstrap a missing billing subscription recover from the uniqueness race without hiding unrelated integrity failures.
- PR #52 and #53 PR-head checks passed. PR #53's real-worker synthetic-media smoke passed and the worker/containers were stopped; this is ephemeral CI evidence, not a persistent production worker.
- Main SHA `e672bf0c5f75441e0bd9556db6811320a33a7a5e` has fresh successful post-merge CI, Security, CodeQL, and Repository Gate evidence. Cloudflare Whisper Preflight passed on its parent SHA `1b6baad0df7f8b0ad5080381143288de62ba16a7`, reaching the deployed Worker handler and receiving the expected JSON method guard (HTTP 405) without audio or Workers AI inference. This is handler reachability evidence only, not authenticated inference or production readiness.

## Historical workflow evidence

The links below document prior runs and their specific test scope; they are not current-main or production-provider acceptance.

### Evidence available at the previous checkpoint

- Cloudflare Whisper Worker deployment workflow succeeded in [run 38035662514](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38035662514). The run validated deployment credentials, deployed the Worker, configured the Worker secret, and completed a handler smoke test without AI inference. This does **not** prove authenticated transcription works.
- CI run [38032221181](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38032221181) reported successful backend, backend-integration, frontend, and E2E jobs.
- Security run [38032221138](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38032221138) reported successful dependency-audit, container-scan, and SAST jobs.
- CodeQL run [38032221149](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38032221149) reported successful Python and JavaScript/TypeScript analysis.
- Repository Gate run [38032221140](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38032221140) succeeded.
- Evidence workflows [backup/restore 38031506652](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506652), [real-worker synthetic-media 38031506679](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506679), [local runtime 38031506677](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506677), [Windows local runtime 38031506685](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506685), and [Windows portable package 38031506640](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506640) reported successful jobs.

These run links are evidence for the specific workflow runs and their tested scope, not a claim that every run used the current default-branch SHA or that production providers passed end-to-end acceptance. Re-check latest main-branch runs before release decisions.

## Historical documentation freshness finding (prior main baseline)

The headers of `ROADMAP.md` and `docs/MASTER_REMAINING_WORK.md` still describe the baseline immediately after PR #43 (main SHA `5da1625c031ec235e636b8875be5bee9d368f7b2`) and include older historical checkpoints. The current default-branch commit observed during this audit is `ae6d3036443262b62271e9012fd78f5b5956ad69` (PR #44). The connector returned no PR-triggered workflow records for that main SHA, so its fresh checks are **not verified here**. Treat older main-checkpoint statements as historical until reconciled against current run evidence; do not mark the main baseline fully green from older evidence alone.

## Historical checkpoint documentation PR validation

The latest checkpoint branch commit checked was `aaf9d95bb87030de651a9d4bd15d3990530e90c5`. The following PR workflow runs completed with conclusion `success` for that commit:

- [Repository Gate 38040010499](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38040010499)
- [CodeQL 38040010522](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38040010522)
- [Security 38040010509](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38040010509)
- [CI 38040010495](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38040010495)

These checks validate the PR branch commit only. They do not replace fresh evidence for the latest default-branch commit, do not constitute a production provider test, and do not prove that a deployed service is healthy. This documentation update will trigger another round of PR checks; verify those before merging.

## Quota-free work queue

### 1. Repository and CI baseline
- [x] Refresh current-main CI, Security, CodeQL, and Repository Gate runs for SHA `e672bf0c5f75441e0bd9556db6811320a33a7a5e`; all succeeded. The non-billable Cloudflare Whisper Preflight last succeeded on parent SHA `1b6baad0df7f8b0ad5080381143288de62ba16a7`.
- [ ] Run fresh main-branch backup/restore, real-worker synthetic-media, local runtime, Windows runtime, and portable-package evidence against `e672bf0c5f75441e0bd9556db6811320a33a7a5e`. These evidence workflows are manual-dispatch or path-triggered; the connected GitHub tool here does not expose workflow dispatch, so existing artifacts below remain tied to their recorded older SHAs.
- [x] Reconcile the top-level current-checkpoint metadata in `ROADMAP.md` and `docs/MASTER_REMAINING_WORK.md` with the current SHA and latest evidence.
- [x] Keep live inference and paid-resource workflows separate from default CI, with explicit manual confirmation and minimal permissions.

### 2. Cloudflare Whisper — no-inference checks only
- [x] Cloudflare API confirms the deployed Worker script exists and has the `AI`, `ALLOWED_ORIGIN`, and secret binding names; the secret value was not read.
- [x] Preflight run [38071946053](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38071946053) reached the Worker handler and received the expected JSON method guard; no audio or Workers AI inference was used.
- [ ] Keep `cloudflare-whisper-live-evidence.yml` undispatched until the owner explicitly approves quota-consuming inference.
- [ ] Authenticated real-audio inference remains unverified; secret binding presence is not proof that GitHub/Render/Cloudflare secret values match.
- [x] Never print secret values, request authorization headers, audio, or raw provider responses in logs/artifacts.

### 3. Free-first worker/runtime strategy
- [x] Review the worker evidence workflow and Kaggle dispatcher configuration statically; no persistent worker was provisioned.
- [x] Confirm the dispatcher unit tests are included by the workflow's `unittest discover -s infra/kaggle -p 'test_*.py'` command.
- [x] Kaggle scheduled dispatch now requires `ENABLE_KAGGLE_DISPATCH=true`; manual dispatch requires `confirm_kaggle_dispatch=true`. Leave disabled unless the owner deliberately opts in.
- [x] Document the free-first local/ephemeral strategy and distinguish ephemeral CI evidence from a persistent production background worker.
- [ ] Do not create a paid Render worker or other billable resource without explicit owner approval.

### 4. Production acceptance dependencies
- [ ] Confirm production database migration head and tenant-scope safety using read-only checks where possible.
- [ ] Validate backup/restore and storage lifecycle in the target environment only when safe credentials, a disposable target, and explicit approval are available.
- [ ] Verify Google OAuth/Drive export, SMTP, Stripe, and Sentry integrations with provider-appropriate non-billable/test modes where available.
- [ ] Complete role/membership/tenant acceptance, accessibility, load/performance, rollback checks, legal/compliance review, and independent penetration testing before production release.

## Evidence and status rules

Use `VERIFIED` only when evidence identifies the exact commit, environment, run, and tested behavior. Keep the following separate:

- source code or configuration exists;
- CI or synthetic test passed;
- service is reachable;
- authenticated provider request passed;
- complete production workflow passed.

Do not infer a later level from an earlier one. The release remains **PENDING — NOT PRODUCTION READY** until the applicable gates have current evidence.
