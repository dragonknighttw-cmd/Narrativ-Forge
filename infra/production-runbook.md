# Narrativ Forge Production Runbook

## 1. Readiness
- Check `GET /health` for process liveness.
- Check `GET /ready` for database and Redis readiness.
- Never treat liveness as worker readiness.

## 2. Stuck processing job
1. Inspect `ProcessingJob.status`, `retry_count`, `next_run_at`, `last_error`.
2. Verify the worker and Redis connection.
3. For a terminal failed job, use the authenticated retry endpoint.
4. Confirm the retry creates/dispatches exactly one real-processing task.
5. Inspect the failed-job/DLQ record if retries are exhausted.

## 3. Export stuck in exporting
1. Inspect the episode and its `ExportRecord`.
2. Do not manually mark exported without a provider manifest.
3. If the provider operation is known to be incomplete, return the episode to the documented retry/failure path.
4. Preserve the audit trail.

## 4. Google Drive
- Verify OAuth connection belongs to the same organization.
- Verify approved episode + approved subtitle + final video asset before export.
- Reuse an existing folder/file identity when the manifest proves it.
- Never store OAuth client secrets or access tokens in source control.

## 5. Storage incident
- Check the primary storage provider.
- If replication is enabled, inspect `StorageReplica` checksum/status.
- A replica is valid only when its checksum matches the primary asset.
- Do not delete the primary copy until retention/lifecycle policy permits it.

## 6. Database restore
- Restore into an isolated environment first.
- Run migrations/schema checks.
- Run unit/integration smoke tests.
- Verify organization isolation and approved-output invariants.
- Only then promote the restored database.

## 7. Secrets
Required production secrets must be supplied through the deployment secret manager/environment:
`SESSION_SECRET`, `OAUTH_ENCRYPTION_KEY`, provider credentials, storage credentials, SMTP credentials, and Stripe secrets where enabled.
Never commit real values to README, roadmap, fixtures, or tests.

## 8. Rollback
- Roll back application deployment before destructive database changes.
- Do not roll back a schema migration blindly if newer writes depend on it.
- Capture the incident, affected job IDs, export IDs, and audit events before remediation.

## 9. Verification boundary
Code readiness is not live-service verification. Real credentials, real media, real worker capacity, OAuth, Stripe, SMTP, backups/restores, and external API limits require environment-level verification.
