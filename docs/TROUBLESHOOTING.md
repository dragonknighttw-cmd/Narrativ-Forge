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
