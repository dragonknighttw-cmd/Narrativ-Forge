# Remaining Work and Owner Actions
**Date:** 2026-10-12 UTC  
**Release status:** PENDING — NOT PRODUCTION READY

## Safe work already completed
- Worker deploy verified successful; deployed version and binding presence confirmed using metadata only.
- Render latest deployment confirmed live and startup logs show HTTP 200 for `GET /`.
- Netlify current deploy and SSO policy rechecked.
- Report pack prepared on a documentation branch; PR checks passed at the previously observed PR head. Recheck checks after the final documentation commits.

## Ordered remaining work

### P0 — Decide release and spend boundaries
- [ ] Review [draft PR #72](https://github.com/dragonknighttw-cmd/Narrativ-Forge/pull/72); do not merge until current checks and Render build implications are understood.
- [ ] Decide whether one-time Netlify redeploy is approved. Current published deploy is stale; no deploy was triggered to conserve build usage.
- [ ] Explicitly approve or decline any quota-consuming authenticated Whisper inference.
- [ ] Explicitly approve or decline paid persistent worker capacity. None has been created.

### P1 — Safe runtime verification
- [ ] Capture fresh GET-only HTTP status and redacted response for Render `/api/v1/health` and `/api/v1/ready`; do not treat historical checks as current.
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
