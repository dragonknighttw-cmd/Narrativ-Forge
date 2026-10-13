# Remaining Work and Owner Actions
**Date:** 2026-10-12 UTC  
**Release status:** PENDING — NOT PRODUCTION READY

## Safe work already completed
- Worker deploy verified successful; deployed version and binding presence confirmed using metadata only.
- Render latest deployment confirmed live and startup logs show `GET /` HTTP 200.
- Render auto-deploy was disabled by the owner. Read-only service metadata confirms `autoDeploy=no` / trigger `off`, and event history records `auto_deploy_disabled` at `2026-10-12T15:30:53Z`. Existing live deployment was not changed.
- Netlify current deploy and SSO policy rechecked.
- Report pack is on [PR #72](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/72), open and ready for review (not merged). CI, Security, CodeQL and Repository Gate passed on prior head `54cb58e1a357e5cae3156d1ca1e2b7cf82661d42`; new runs triggered by report refresh commits are pending. Check [PR #72](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/72) for the current results.

## Ordered remaining work

### P0 — Decide release and spend boundaries
- [ ] Review PR #72 after latest checks complete; do not merge until Render build implications are understood.
- [x] Disable Render auto-deploy on `main` to reduce automatic builds. Confirmed via service metadata and `auto_deploy_disabled` event. Future releases require intentional Manual Deploy.
- [ ] Decide whether one-time Netlify redeploy is approved. Current published deploy is stale; no deploy was triggered to conserve build usage.
- [ ] Explicitly approve or decline any quota-consuming authenticated Whisper inference.
- [ ] Explicitly approve or decline paid persistent worker capacity. None has been created.

### P1 — Safe runtime verification
- [ ] Capture fresh GET-only HTTP status and redacted response for Render `/api/v1/health` and `/api/v1/ready`; available probe/web access could not reach the URLs, and Render request logs returned no entries. Endpoint status remains unknown.
- [ ] Confirm worker architecture and queue ownership; API service metadata alone does not establish a continuous media worker.
- [ ] Verify auth, rate limits, CORS/origin policy and cross-tenant isolation without disclosing credentials.
- [ ] Confirm database migration head and managed backup/restore procedures.

### P2 — Controlled end-to-end acceptance (approval required where quota may be used)
- [ ] Run synthetic audio through the intended pipeline first.
- [ ] With owner approval, run a short approved sample through Whisper; record model/provider, duration, request size, response, latency and cost/quota impact.
- [ ] Have a human review Burmese transcript against a reference and compute WER/CER where reference text exists.
- [ ] Verify subtitle timing, Unicode normalization, clipping, retry/idempotency, DLQ and provider fallback.

### P3 — Production readiness
- [ ] Verify Google Drive OAuth/export/recovery, SMTP, Stripe, Sentry and storage lifecycle.
- [ ] Run performance/load and accessibility/WCAG review.
- [ ] Complete privacy/legal/commercial-provider terms review and independent security/penetration review.
- [ ] Test operational alerts, rollback, backup restoration and incident response.
- [ ] Revisit the release decision only after evidence for each gate is recorded.

## Local work
Windows/local testing remains deliberately deferred at the user's request. Do not infer local readiness from cloud evidence.
