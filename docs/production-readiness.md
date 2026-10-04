# Narrativ Forge — Production Readiness

## Runtime gates

- Set `APP_ENV=production`.
- Set a random `SESSION_SECRET` of at least 32 characters.
- Set `SESSION_COOKIE_SECURE=true`.
- Set exact `CORS_ORIGINS` and `TRUSTED_HOSTS`; do not use wildcards.
- Configure `OAUTH_ENCRYPTION_KEY` with a generated Fernet key and keep it outside Git.
- Configure Google OAuth redirect URI to the deployed HTTPS callback.
- Deploy the Next.js frontend on Netlify and set `NEXT_PUBLIC_API_BASE_URL` to the Render API origin.
- Deploy the FastAPI API and real-processing worker on Render with the same application revision.
- Use PostgreSQL for production rather than the SQLite development default.
- Provision managed PostgreSQL and Redis and configure both services securely; see the [managed services provisioning guide](../infra/managed-services.md).
- Use Backblaze B2 as the production media object store (`STORAGE_PROVIDER=b2`); Render local disk is only temporary processing space.
- Configure a private B2 bucket, bucket-scoped S3-compatible application key, region, and endpoint. Keep B2 credentials outside Git.
- Persist each asset's storage provider, immutable object key, SHA-256 checksum, and byte size in PostgreSQL.
- Source, processed, transcript, and future revisions use separate versioned object keys; source objects are never overwritten by processing.
- Put a real edge/proxy rate limiter in front of the API. The application has a small in-process baseline limiter, but it is not shared across multiple workers/instances.

## Security controls implemented

- Signed, expiring httpOnly session cookies.
- Bearer session validation for API clients.
- Production startup rejects insecure session defaults.
- Trusted host validation.
- Explicit CORS allowlist.
- Security response headers.
- Login/upload/basic request rate limiting.
- Server-side Google OAuth token encryption.
- Narrow Google Drive `drive.file` scope.
- Upload MIME/extension validation and filename sanitization.
- Approval and export audit events.
- Approved subtitles are immutable; revisions create new versions.
- Export is gated by approval, final asset, and approved subtitle.
- Google Drive export persists partial progress and retries without intentionally creating duplicate files.

## Real-processing retry and dead-letter handling

Real-processing retries are scheduled in PostgreSQL and dispatched when due.
The initial execution may be followed by at most three automatic retries, with
deterministic delays of 60, 120, and 240 seconds (capped at one hour). Failed
attempt details remain in `last_error`; an exhausted job is recorded in
`failed_jobs`, audited in `audit_events`, and published as a notification to
the Celery `dead_letter` queue. The database record remains the durable source
of truth if Redis is unavailable during notification publication.

Authorized manual retry preserves the processing job ID. For a job below its
automatic retry limit it does not consume another automatic retry; recovering
an exhausted job resolves its active failed-job record and resets the retry
counter. A worker crash can still leave a job in `running`; automatic abandoned
job recovery is not implemented.

## Real-processing worker concurrency

`WORKER_MAX_CONCURRENCY` configures the Celery worker's bounded process pool
and a process-shared semaphore used only by real-processing tasks; it defaults
to `1`. Values must be positive integers; zero, negative, and non-integer
values fail configuration validation. Both limits together cap expensive work
at the lower of the pool size and semaphore limit; the semaphore protects the
per-instance limit if the Celery pool is configured larger. The setting limits
work per Celery worker instance, not across the deployment: three instances
set to `1` can process up to three jobs concurrently. Each running task
occupies one pool slot until real processing, including timeout process
cleanup, returns. Jobs beyond available slots wait for Celery capacity instead
of starting more processing subprocess trees. This limits concurrent
FFmpeg/Whisper process trees, not threads or resource usage inside one such
process. The worker pool is shared with dead-letter notifications, which do not
acquire the processing semaphore.

## Prometheus metrics

The API exposes aggregate metrics at the public `/metrics` endpoint. It
reports API HTTP request counts and durations by bounded method, route
template, and status-class labels; worker lifecycle events, timeouts, and
processing duration are aggregated in the existing shared Redis service.
Queued real-processing depth is read from PostgreSQL and distinguishes due
jobs from future-scheduled retries. Do not add job IDs, user data, filenames,
exception text, or raw request paths to metric labels. The endpoint is
unauthenticated for scraper access and must expose aggregate telemetry only.
Worker metric writes are best-effort and use bounded Redis timeouts; Redis
scrape-source or database errors return a generic `503` from `/metrics`.

## Resumable asset uploads

Asset uploads can use persisted sessions at `/api/v1/uploads`, with explicit
part numbers and byte offsets. The API streams each request into a bounded
single-part buffer, stores part checksums and provider ETags, and only creates
an asset after all contiguous parts have been verified and completed. The
default part size is 8 MiB; configure `UPLOAD_CHUNK_SIZE_BYTES` at 5 MiB or
larger for B2 compatibility. `UPLOAD_SESSION_TTL_SECONDS` defaults to 24 hours.
The existing `MAX_UPLOAD_SIZE_BYTES` limit remains in force, and uploads are
also capped by the signed 32-bit size limit of the current Asset schema.
Session ownership is enforced on resume, chunk, commit, and abort operations.
Expired sessions are rejected and their provider multipart upload is aborted
when the expired session is next accessed; incomplete uploads abandoned without
another API request require storage-provider lifecycle cleanup.

## Backup and restore

SQLite development backup:

```bash
DATABASE_URL=sqlite:///./narrativ_forge.db BACKUP_DIR=./backups python scripts/backup_db.py
DATABASE_URL=sqlite:///./narrativ_forge.db python scripts/restore_db.py ./backups/<backup>.db
```

PostgreSQL production backup:

```bash
DATABASE_URL="$PRODUCTION_DATABASE_URL" BACKUP_DIR=./backups python scripts/backup_db.py
DATABASE_URL="$PRODUCTION_DATABASE_URL" python scripts/restore_db.py ./backups/<backup>.dump
```

Run a restore drill before launch and periodically afterward. Keep backups outside the application container and test that media/source files referenced by the DB are also recoverable.

## Deployment sequence

1. Run backend tests and frontend typecheck/build.
2. Run browser E2E against the release candidate.
3. Apply a database migration for the release before starting application workers.
4. Deploy API and worker with the same application revision.
5. Configure production secrets and exact origins/hosts.
6. Verify health, login, upload, processing, subtitle, approval, mock export, and audit history.
7. Run a small real-media FFmpeg/Whisper smoke test.
8. Verify backup creation and restore in the target database environment.
9. Verify Google OAuth/Drive export with a test Drive account before enabling production exports.
10. Monitor processing failures and export failures; failed jobs must remain inspectable and retryable.

Only `APP_ENV=development` may create tables automatically at application startup. Production and staging must apply `alembic upgrade head` before starting the API or worker. The automated migration-path tests currently use SQLite; they do not establish PostgreSQL compatibility.

## Current explicit pre-launch blockers

- Production authentication is now database-backed with PBKDF2 password hashes, signed expiring sessions, owner/editor/viewer roles, and owner-only invites. The first owner is created explicitly with `scripts/bootstrap_admin.py`; remove bootstrap secrets after provisioning.
- Alembic is now the production schema migration mechanism. The first baseline is `0001_bootstrap`; every subsequent schema change must ship as a reviewed Alembic revision.
- Real Google Drive OAuth/export and real FFmpeg/Whisper require environment-level credentials/binaries and have not been proven by CI.
- Render + Netlify are now the target deployment providers, with Backblaze B2 as the shared durable media store for both API and worker.
- B2 credentials/bucket configuration and a real upload/download/delete smoke test still require environment-level provisioning; no cloud credentials are stored in the repository.
