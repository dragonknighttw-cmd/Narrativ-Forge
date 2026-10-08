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
