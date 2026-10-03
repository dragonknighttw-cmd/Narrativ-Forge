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
- Use Redis as the shared service for future background-job processing; Phase 1 CI provisions Redis so integration environments match the target foundation.
- Run Alembic migrations explicitly before application startup; the application does not use schema creation as a production deployment mechanism.
- Configure `SENTRY_DSN` when error reporting is enabled; Sentry is initialized without sending default PII.
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

## Current explicit pre-launch blockers

- Production authentication is now database-backed with PBKDF2 password hashes, signed expiring sessions, owner/editor/viewer roles, and owner-only invites. The first owner is created explicitly with `scripts/bootstrap_admin.py`; remove bootstrap secrets after provisioning.
- Alembic is now the production schema migration mechanism. The first baseline is `0001_bootstrap`; every subsequent schema change must ship as a reviewed Alembic revision.
- Real Google Drive OAuth/export and real FFmpeg/Whisper require environment-level credentials/binaries and have not been proven by CI.
- Render + Netlify are now the target deployment providers, with Backblaze B2 as the shared durable media store for both API and worker.
- B2 credentials/bucket configuration and a real upload/download/delete smoke test still require environment-level provisioning; no cloud credentials are stored in the repository.
