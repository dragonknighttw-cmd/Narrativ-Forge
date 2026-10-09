# Troubleshooting

> Owner: Operations maintainers  
> Update when: recurring failure modes or recovery procedures change  
> Last Updated: 2026-10-08  
> Do NOT put here: secrets or credentials

## Stuck processing job

1. Inspect job status/retry/error fields.
2. Verify worker and Redis/delivery health.
3. Verify source asset exists.
4. Use the authenticated retry endpoint for failed jobs.
5. Verify one dispatch and one output.
6. If retries are exhausted, inspect failed-job/DLQ state.

Do not delete the source asset or directly edit job completion state.

## Export stuck

Inspect episode/export record and provider manifest. Do not mark exported without provider evidence. Reuse deterministic remote identities when the manifest supports recovery.

## Storage incident

Check provider availability, object key, checksum, and replica/reference state. Do not delete the primary copy until retention/reference policy permits it.

## Database restore

Restore into isolation first. Verify migration history, critical tables, tenant isolation, storage references, health, and application behavior before enabling writes.

## Secret rotation

Rotate through the deployment/provider secret stores. Never paste secrets into tickets, chat, logs, tests, or documentation.

## Verification boundary

If a failure depends on a real provider, worker, credential, mailbox, or production environment, classify it VERIFY/PENDING rather than inferring success from local tests.

## Media pipeline failure modes

### Job stuck
- Inspect PostgreSQL `ProcessingJob`.
- Check Redis/Celery worker heartbeat.
- Check worker logs.
- If lease expired, use stale-job recovery/retry.
- If retries are exhausted, inspect `FailedJob`/DLQ.

### Whisper timeout
- Preserve the processing job.
- Record the provider failure.
- Retry within policy.
- If cloud Whisper is unavailable/over threshold, use local Whisper fallback.
- Never mark subtitle processing complete without valid output.

### Storage write failure
- Keep source asset.
- Retry provider write.
- Verify checksum after retry.
- Do not delete the primary copy until references/recovery are confirmed.

### Provider outage
- Mark provider operation failed.
- Apply configured fallback where supported.
- Record provider and failure reason.
- Do not silently switch a provider when commercial/quality policy forbids it.

### Worker unavailable
- Queue remains the durable pending boundary.
- Do not fake completion from the API.
- Provision/restart worker and verify Celery heartbeat before replaying production jobs.


## Cloudflare Whisper returns HTTP 403 before authentication

Latest evidence: [live run #37907157973](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/runs/37907157973) returned HTTP 403 with `Content-Type: text/plain`, a Cloudflare `CF-Ray`, and no recognized Worker JSON error. The authenticated request and AI inference were never reached.

1. Run [Cloudflare Whisper Preflight](https://github.com/dragonknighttw-cmd/Narrativ-Forge/actions/workflows/cloudflare-whisper-preflight.yml). It sends an unauthenticated GET only—no audio, secret, or Workers AI inference.
2. Expected result: HTTP 405 with JSON `{"error":"Method not allowed"}`. This proves the public URL reached the Worker handler's method guard, not that authentication or inference works.
3. If the result is HTTP 403 `text/plain` with a `CF-Ray`, capture the Ray ID and timestamp and inspect Cloudflare account/edge access controls, the workers.dev hostname, and the deployed Worker script/version. Do not rotate the shared secret based only on this result.
4. If the result is JSON `403 Origin not allowed`, compare the deployed `ALLOWED_ORIGIN` binding with `web-platform/cloudflare/whisper-worker/wrangler.jsonc`.
5. Only diagnose a secret mismatch after the unauthenticated request reaches the Worker and returns the expected 401, then an authenticated request returns 401. That authenticated request may require an approved inference test.
6. Never include secret values, bearer tokens, or transcript text in logs or screenshots. Do not repeat live inference until the non-billable preflight passes and quota use is explicitly approved.
