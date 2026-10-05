# Stuck processing job runbook

## Scope

Use this runbook when a real_processing job remains queued, running, or failed unexpectedly.

## Safety rules

- Do not delete the original source asset.
- Do not manually mark a job completed unless the output asset and database state are verified.
- Do not paste secrets into tickets, logs, or chat.
- Keep the Render deployment free-only; do not add a paid worker without explicit approval.

## Diagnosis

1. Check the job through GET /api/v1/jobs/<job_id>.
2. Inspect the Render API logs for the job ID.
3. If a dedicated Celery runtime is available, inspect worker logs for narrativ.process_real_job.
4. Check Redis connectivity and queue health.
5. Check the source asset exists in its declared storage provider.

## Recovery

### Queued

A queued job is eligible for the Celery beat recovery dispatcher. If a worker runtime is healthy, it should be dispatched automatically.

For an emergency manual dispatch from a worker environment:

    PYTHONPATH=. python -c "from app.workers.tasks import enqueue_real_job; print(enqueue_real_job('<JOB_ID>'))"

### Failed

Use the application retry endpoint:

    POST /api/v1/jobs/<JOB_ID>/retry

Do not edit the database directly.

### Running too long

Confirm whether FFmpeg/Whisper is still active before taking action. The processing service has a process-group timeout and cleanup path. If the worker host itself is unhealthy, restart the worker runtime rather than deleting the job.

## Escalation

Capture:

- job ID
- episode public ID
- current job status
- retry count
- error code/message
- worker/runtime timestamp
- relevant Sentry event ID

Never capture OAuth refresh tokens, API keys, or session cookies.
