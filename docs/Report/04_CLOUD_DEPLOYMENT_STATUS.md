# Cloud Deployment Status

**Generated:** 2026-10-13  
**Application-code checkpoint:** `main`, `dfff46a5335833723e403b70fa54ff8ba8cc0100` (PRs #72 and #73 merged)

## Fresh post-merge verification

- GitHub Actions CI, Security, CodeQL and Repository Gate passed on the exact application-code checkpoint above. Later documentation-only updates are separate commits and must have their own latest workflow results checked before declaring the latest docs commit green.
- Isolated Linux regression tests at that exact SHA: focused Whisper/subprocess tests **17 passed**; backend unit/security selection **303 passed, 3 skipped, 84 deselected**; Cloudflare Whisper Worker contract tests **5 passed**.
- Render read-only metadata confirms service `Narrativ-Forge` is on the free plan, `autoDeploy=no` / trigger `off`, and not suspended. The latest live deploy record remains commit `95aa9163cc40383a8c44c3a5f445e4de899116e4`; no deploy was triggered.
- GET-only attempts to read `/api/v1/health` and `/api/v1/ready` were inaccessible through the available web probe. Render request-log queries for those paths and for all request logs on 2026-10-13 returned no entries. These results do **not** prove the endpoints are down or healthy; current endpoint status remains unknown.
- No Cloudflare inference, quota-consuming request, production deployment, paid worker provisioning, or production-data mutation was performed.

Historical evidence below remains tied to the exact SHAs and dates recorded.

## Documented workflow results

The repository's [local runtime follow-up](../LOCAL_RUNTIME_FOLLOW_UP.md) documents PASS on `b374df9e1e455e35eaa9847d78fb7c9af70f2393` for:

- CI: [#38201576482](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576482)
- Security: [#38201576514](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576514)
- CodeQL: [#38201576494](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576494)
- Repository Gate: [#38201576503](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576503)
- Ephemeral Real Worker: [#38201576538](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576538)
- Windows Portable Package: [#38201576528](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576528)
- Windows Local Runtime: [#38201576459](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576459)
- Local Runtime: [#38201576477](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38201576477)

These are source-document-recorded results for that SHA, not a fresh check of this report's local HEAD. The ephemeral worker workflow is not a persistent production worker.

## Provider and deployment observations

- **Netlify read-only recheck (2026-10-13):** published deploy `6ac4f8aba9c7aa00082031dc` is `ready`, created 2026-10-06, and still points to commit `777fba6ca92ce59e53e741b976bc9ea9692b45c1` on `main`. SSO team login remains required for all projects. No Netlify deploy was triggered.

The dated repository evidence records:

- Render `/api/v1/health` and `/api/v1/ready` returned HTTP 200, with database and Redis ready, during a prior non-billable check. No endpoint was probed in this task.
- Cloudflare Whisper GET-only preflight returned the expected worker JSON 405; that confirms the handler's method guard only and did not submit audio or invoke inference.
- Earlier authenticated Whisper evidence failed before inference with HTTP 403 rather than the expected 401. No authenticated transcription success is documented.
- The latest documented Netlify read-only audit found a ready deployment at older commit `777fba6ca92ce59e53e741b976bc9ea9692b45c1`; this was not rechecked here.
- The Render API exists in the deployment records. A continuously running background media worker is not established; provisioning it may incur cost and requires owner approval.

Sources: [`CURRENT_STATE.md`](../../CURRENT_STATE.md), [`MASTER_REMAINING_WORK.md`](../MASTER_REMAINING_WORK.md), [`DEPLOYMENT.md`](../DEPLOYMENT.md), and [`LOCAL_RUNTIME_FOLLOW_UP.md`](../LOCAL_RUNTIME_FOLLOW_UP.md).

## Status

Live deployment, live health, GET-only reachability, authenticated inference, persistent worker operation, and production acceptance are separate claims. Only the specific dated evidence above is documented; current cloud state is **NOT VERIFIED** in this task. Overall status remains **PENDING — NOT PRODUCTION READY**.
