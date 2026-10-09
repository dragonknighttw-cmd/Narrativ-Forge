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


## Kaggle ephemeral dispatcher configuration and recovery

The scheduled dispatcher is a best-effort, quota-sensitive fallback. It checks PostgreSQL for a due `real_processing` job before querying/pushing the Kaggle kernel. A successful run that reports no queued work means no Kaggle session was launched.

### Required GitHub Actions settings

Open **Repository → Settings → Secrets and variables → Actions** for this repository. Configure repository-level entries (not an Environment-only variable unless the workflow is explicitly assigned to that Environment):

- **Variable** `KAGGLE_KERNEL_ID`: `thuwon/narrativ-forge` (owner/kernel-slug format; use the exact kernel owner and slug shown by Kaggle).
- **Secret** `KAGGLE_DISPATCH_DATABASE_URL`: PostgreSQL connection URI for the dispatch database, from the Supabase project's database connection details.
- **Secret** `KAGGLE_API_TOKEN`: Kaggle API token supported by the installed Kaggle CLI.

The workflow accepts `KAGGLE_KERNEL_ID` as either a repository Actions variable or a repository Actions secret. Prefer the variable because the kernel ID is not a credential. Do not put database URLs or API tokens in variables, source files, workflow output, issues, or chat.

After changing settings, a workflow run only proves the settings are present if the configuration preflight step passes. It does not prove the database schema, Kaggle access, kernel execution, or media processing works.

### Failure triage

- `KAGGLE_KERNEL_ID is empty`: confirm the exact name and repository scope; if it was created under an Environment, move it to repository Actions variables or configure a matching repository secret. The workflow intentionally does not print its value.
- `Missing Actions secret KAGGLE_DISPATCH_DATABASE_URL`: verify the secret name and scope; use the PostgreSQL connection URI, not the Supabase HTTPS project URL.
- Database connection or `processing_jobs` query failure: verify the URI, password URL-encoding, network/pooler option, and that the target schema has the expected `processing_jobs` fields. Never run destructive SQL to troubleshoot.
- Kaggle status lookup failure: verify the token and that the token owner can access the exact kernel ID. The dispatcher fails closed rather than pushing when status cannot be identified.
- `No due real_processing jobs are queued`: the configuration check may be successful; the dispatcher intentionally exits without launching Kaggle.
- `Kaggle kernel status` is active: duplicate dispatch is skipped. A terminal state may permit a new push if due work remains.

### Quota and production boundaries

The scheduled workflow runs every ten minutes and may launch Kaggle compute when due work is queued. Inspect logs and queue state before manually rerunning it. Do not use production media for a diagnostic run. A successful push is not proof of worker completion or end-to-end media processing; verify job state, worker logs, and output separately. No production-ready claim is allowed without linked live evidence.
