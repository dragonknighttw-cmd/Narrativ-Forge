# Narrativ Forge — Production Worker Runtime

## Purpose
Narrativ Forge keeps the API service separate from heavy media processing. Celery workers consume the Redis queue and run FFmpeg/Whisper/real-processing tasks.

## Current production state
- API: Render Web Service
- Broker: Upstash Redis
- Worker runtime: repository-ready, but not provisioned on the current free-only Render plan
- Worker image: `web-platform/backend/Dockerfile.worker`
- Dispatcher: `python -m app.workers.real_worker`
- Celery app: `app.workers.celery_app:celery_app`

Do not deploy the worker as a normal API process. It must run as a long-lived worker process with access to FFmpeg and the same production environment variables.

## Queue semantics
Celery is configured with late acknowledgements, worker-lost task rejection, prefetch multiplier 1, broker connection retry on startup, and task-started tracking.

The database remains the source of truth for processing state. A DB claim prevents duplicate execution even if a broker message is redelivered.

## Retry / DLQ flow
```text
queued -> worker claims job -> real processing
                           -> completed
                           -> failed -> exponential retry
                                      -> retry budget exhausted
                                      -> failed_jobs record
                                      -> dead_letter queue
```

Retry delays are 60s, 120s, 240s ... capped at 3600s. Manual retry reuses the same processing-job identity and resolves the active failed-job record.

## Production smoke test after worker provisioning
1. Create one real processing job.
2. Confirm the job enters Redis/Celery.
3. Confirm worker logs show task receipt.
4. Confirm DB transitions queued -> running -> completed.
5. Restart a worker during a test job and confirm late acknowledgement/redelivery.
6. Force a deterministic processing failure and verify retry scheduling.
7. Exhaust retries and verify one active failed_jobs record plus DLQ publication.
8. Confirm duplicate dispatch does not create duplicate processing output.
9. Verify FFmpeg output and Whisper subtitle output.

## Free-only constraint
The current Render blueprint intentionally provisions only the web service. Do not silently add a billable Render Background Worker. The remaining production worker gate requires either a user-approved paid/background worker deployment or another always-on worker host that can run FFmpeg/Celery within the project's constraints.