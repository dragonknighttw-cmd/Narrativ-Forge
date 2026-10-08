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

## Worker runtime requirements — release gate

**Status: BLOCKED until a continuous worker runtime is provisioned.**

### Required runtime

- CPU: start with **1 shared/standard CPU**.
- Memory: **at least 2 GB** for the first real-media test; increase if Whisper/FFmpeg workloads exceed the limit.
- OS: Linux container.
- FFmpeg + ffprobe installed.
- OpenAI Whisper installed from `requirements-real-processing.txt`.
- Redis reachable through `REDIS_URL`.
- PostgreSQL reachable through `DATABASE_URL`.
- Storage provider credentials matching `STORAGE_PROVIDER`.
- Cloudflare Whisper URL/shared secret when cloud transcription is enabled.
- `WORKER_MAX_CONCURRENCY=1` for initial verification.

### Entrypoint

```
celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --concurrency=1 --beat
```

### Health

A background worker does not expose an HTTP health endpoint. Health must be proven with:
1. Celery worker heartbeat/inspect ping.
2. Redis broker connectivity.
3. A known test task accepted and completed.
4. Worker logs showing task execution.
5. PostgreSQL job state and output verification.

Do not treat the API health endpoint as worker health.

### Scaling

Start with one worker and concurrency 1. Increase worker count/concurrency only after representative media runtime and memory measurements. Beat must remain singleton to avoid duplicate scheduled cleanup.

### Failure/recovery

Late acknowledgements, worker-loss rejection, bounded concurrency, retry backoff, stale-job recovery and failed-job/DLQ publication are implemented in the repository. They still require live failure-injection evidence before release.
