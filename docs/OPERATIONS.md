# Operations

> Owner: Operations maintainers  
> Update when: worker/runtime/recovery procedures change  
> Last Updated: 2026-10-08  
> Do NOT put here: secret values

## Runtime

The API is separate from heavy processing. The repository worker uses the canonical Celery application and real-processing task path. PostgreSQL remains the durable job-state source of truth.

Free-first runtime options are local Windows workers, ephemeral Kaggle execution, and configured delivery services. A paid always-on worker is reserved.

## Queue/recovery semantics

Use late acknowledgements, worker-loss recovery, bounded concurrency, explicit processing timeouts, stale-job recovery, retries, and DLQ handling as configured in the repository.

Representative flow:

`queued → running → completed`

or

`queued → running → failed → retry → failed_jobs/DLQ`

Never mark a processing job completed without verified output and database state.

## Runbooks

- Stuck job: diagnose job state, queue, worker, source asset; use the retry endpoint rather than direct DB edits.
- Restore: restore to an isolated target, verify migration history, critical tables, tenant isolation, storage references, then enable writes.
- Secret rotation: update provider/deployment stores, restart affected services, verify through non-secret checks, then revoke old credentials.
- Production incident: preserve job/export/audit identifiers and never capture credentials.

## Operational gates

Real worker, real media, retry/DLQ/failover, storage lifecycle, backup/restore, monitoring/alerts, and production integrations require live evidence.
