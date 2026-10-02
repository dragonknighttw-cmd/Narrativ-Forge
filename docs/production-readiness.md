# Narrativ Forge — Production Readiness

## Runtime gates

- Set `APP_ENV=production`.
- Set a random `SESSION_SECRET` of at least 32 characters.
- Set a non-default `DEV_AUTH_PASSWORD` and treat it as an environment secret.
- Set `SESSION_COOKIE_SECURE=true`.
- Set exact `CORS_ORIGINS` and `TRUSTED_HOSTS`; do not use wildcards.
- Configure `OAUTH_ENCRYPTION_KEY` with a generated Fernet key and keep it outside Git.
- Configure Google OAuth redirect URI to the deployed HTTPS callback.
- Use PostgreSQL for production rather than the SQLite development default.
- Store uploaded media on durable storage or a mounted persistent volume; never depend on ephemeral container storage for source assets.
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
- Durable object/media storage and deployment provider configuration still need to be selected.
