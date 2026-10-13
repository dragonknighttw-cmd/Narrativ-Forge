# Test Results
**Date:** 2026-10-12 UTC  
**Release:** PENDING — NOT PRODUCTION READY

Status meanings: PASS = direct evidence observed; FAIL = observed failure; BLOCKED = prerequisite/capability missing; NOT RUN = intentionally not executed; NOT VERIFIED = evidence insufficient.

| Area | Status | Evidence / limitation |
|---|---|---|
| Cloudflare Worker deploy | PASS | [Workflow #38260359375](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38260359375) concluded success on main SHA `95aa9163cc40383a8c44c3a5f445e4de899116e4`. |
| Worker handler/method guard | PASS (limited smoke) | Workflow verifies handler behavior without AI inference; does not establish transcription quality. |
| Worker binding presence | PASS (metadata only) | `AI`, `ALLOWED_ORIGIN`, and `NARRATIV_SHARED_SECRET` bindings present; values not read. |
| Render deploy | PASS | Latest deployment live on main SHA `95aa9163cc40383a8c44c3a5f445e4de899116e4`; startup logs show `GET /` returned HTTP 200. |
| Render `/api/v1/health` and `/api/v1/ready` after latest deploy | NOT RUN / NOT VERIFIED | No fresh post-deploy GET result captured in this review. Historical checks must not be treated as fresh evidence. |
| Netlify deploy artifact | PASS / STALE | Deploy `6ac4f8aba9c7aa00082031dc` is ready but uses old source commit `777fba6ca92ce59e53e741b976bc9ea9692b45c1`. |
| Netlify SSO policy | PASS | Project metadata says team SSO is required for all projects; no access policy changed. |
| PR checks | PASS | Latest observed PR-head checks: [CI #38261893038](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38261893038), [Security #38261893058](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38261893058), [CodeQL #38261893022](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38261893022), [Repository Gate #38261893052](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/38261893052), all success on `7e0bf2a3`. New report commits will trigger new checks; re-check before merge. |
| Fresh Windows/local test | NOT RUN | User requested local work be deferred. See existing `LOCAL_WINDOWS_UNICODE_RUNTIME_REPORT.md` for historical evidence and its limitations. |
| Real audio / Burmese transcription / WER | NOT RUN | Would consume AI/provider quota; requires owner approval and a reviewed reference transcript. |
| Persistent worker / retry / DLQ / failover | BLOCKED / NOT RUN | No continuously running worker or live failure drill confirmed. |
| Managed production backup and restore | NOT VERIFIED | CI/ephemeral restore evidence is not a production recovery drill. |

## Test boundary
This report records only observed evidence. A successful deploy is not a production-readiness certificate. No AI inference, paid resource creation, production data mutation, or local machine test was performed for this cloud-only review.
