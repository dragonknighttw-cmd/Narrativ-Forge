# Free-first production-readiness checkpoint

**Checkpoint date:** 2026-10-10 UTC  
**Release status:** PENDING — NOT PRODUCTION READY  
**Policy:** Do not run Cloudflare Whisper live inference, consume provider quota, or provision potentially billable resources without explicit owner approval.

This checkpoint is a concise operational supplement to `ROADMAP.md` and `docs/MASTER_REMAINING_WORK.md`. It does not replace either document or mark any external integration as production-verified.

## Verified evidence available at this checkpoint

- Cloudflare Whisper Worker deployment workflow succeeded in [run 38035662514](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38035662514). The run validated deployment credentials, deployed the Worker, configured the Worker secret, and completed a handler smoke test without AI inference. This does **not** prove authenticated transcription works.
- CI run [38032221181](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38032221181) reported successful backend, backend-integration, frontend, and E2E jobs.
- Security run [38032221138](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38032221138) reported successful dependency-audit, container-scan, and SAST jobs.
- CodeQL run [38032221149](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38032221149) reported successful Python and JavaScript/TypeScript analysis.
- Repository Gate run [38032221140](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38032221140) succeeded.
- Evidence workflows [backup/restore 38031506652](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506652), [real-worker synthetic-media 38031506679](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506679), [local runtime 38031506677](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506677), [Windows local runtime 38031506685](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506685), and [Windows portable package 38031506640](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38031506640) reported successful jobs.

These run links are evidence for the specific workflow runs and their tested scope, not a claim that every run used the current default-branch SHA or that production providers passed end-to-end acceptance. Re-check latest main-branch runs before release decisions.

## Documentation freshness finding

The headers of `ROADMAP.md` and `docs/MASTER_REMAINING_WORK.md` still describe the baseline immediately after PR #43 (main SHA `5da1625c031ec235e636b8875be5bee9d368f7b2`) and include older historical checkpoints. The current default-branch commit observed during this audit is `ae6d3036443262b62271e9012fd78f5b5956ad69` (PR #44). Treat the existing documents' older “current main” references as historical until reconciled against fresh run evidence. Do not mark the main baseline fully green from the older evidence alone.

## Checkpoint documentation PR validation

The documentation branch head `3d63b035daccd9359191b600086c1a892908d4a3` was checked by the following pull-request workflow runs, all with conclusion `success`:

- [Repository Gate 38038943299](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38038943299)
- [CodeQL 38038943307](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38038943307)
- [Security 38038943302](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38038943302)
- [CI 38038943311](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38038943311)

These checks validate the earlier PR branch commit only. The latest checkpoint edits trigger fresh checks and must be validated separately. PR checks do not replace fresh evidence for the latest default-branch commit, do not constitute a production provider test, and do not prove that a deployed service is healthy.

## Quota-free work queue

### 1. Repository and CI baseline
- [ ] Refresh the latest Actions runs on `main`; record the exact head SHA and conclusion for CI, Security, CodeQL, Repository Gate, backup/restore, worker evidence, local runtime, Windows runtime, and package evidence.
- [x] Run CI, Security, CodeQL, and Repository Gate on the initial documentation PR head; all four passed on that commit.
- [ ] Investigate and fix only confirmed failures; do not repeat already-successful deployment/configuration steps without a reason.
- [ ] Reconcile the top-level “current checkpoint” metadata in `ROADMAP.md` and `docs/MASTER_REMAINING_WORK.md` to the latest main SHA and current evidence before using either as a release-status source.
- [ ] Keep live inference and paid-resource workflows separate from default CI, with explicit manual confirmation and minimal permissions.

### 2. Cloudflare Whisper — no-inference checks only
- [x] Deploy the Worker and configure `NARRATIV_SHARED_SECRET` from the protected GitHub Environment secret.
- [x] Run a non-inference handler smoke test after deployment.
- [x] Review the live-evidence workflow statically: it requires the explicit `confirm_live_inference` boolean to be true and is not part of this audit.
- [ ] Keep `cloudflare-whisper-live-evidence.yml` undispatched until the owner explicitly approves quota-consuming inference.
- [ ] Continue only with safe static review and GET/preflight checks that do not send audio or call the AI binding.
- [ ] Never print secret values, request authorization headers, audio, or raw provider responses in logs/artifacts.

### 3. Free-first worker/runtime strategy
- [x] Review the worker evidence workflow and Kaggle dispatcher configuration statically; no worker was launched.
- [x] Confirm the dispatcher unit tests are included by the workflow's `unittest discover -s infra/kaggle -p 'test_*.py'` command.
- [ ] Clearly distinguish ephemeral CI synthetic-media tests from a persistent production background worker.
- [ ] Document the cheapest viable execution path, its limits, persistence assumptions, and owner actions before enabling a runtime.
- [ ] Decide separately whether unattended scheduled Kaggle launches should be gated behind an explicit boolean confirmation. The current `.github/workflows/kaggle-worker.yml` schedule is `*/10 * * * *`; its final step runs `infra/kaggle/dispatch.py`, which can push a Kaggle session when due `real_processing` jobs are queued and the kernel is not active. Do not manually dispatch it during a no-quota audit. Adding a gate would change automatic queue processing and should be a deliberate owner decision.
- [ ] Do not create a paid Render worker or other billable resource without explicit owner approval.

### 4. Production acceptance dependencies
- [ ] Confirm production database migration head and tenant-scope safety using read-only checks where possible.
- [ ] Validate backup/restore and storage lifecycle in the target environment only when safe credentials, a disposable target, and explicit approval are available.
- [ ] Verify Google OAuth/Drive export, SMTP, Stripe, and Sentry integrations with provider-appropriate non-billable/test modes where available.
- [ ] Schedule accessibility, load/performance, legal/compliance review, and independent penetration testing before production release.

## Evidence and status rules

Use `VERIFIED` only when evidence identifies the exact commit, environment, run, and tested behavior. Keep the following separate:

- source code or configuration exists;
- CI or synthetic test passed;
- service is reachable;
- authenticated provider request passed;
- complete production workflow passed.

Do not infer a later level from an earlier one. The release remains **PENDING — NOT PRODUCTION READY** until the applicable gates have current evidence.
