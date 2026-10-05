# Database restore runbook

## Goal

Restore the production PostgreSQL database without silently mixing old database state with newer application code.

## Before restore

- Put the application into maintenance/read-only mode if available.
- Identify the backup timestamp and target recovery point.
- Record the current application commit.
- Preserve the current database if possible before replacing it.
- Never test restore procedures against the only production copy.

## Restore sequence

1. Provision or identify a clean PostgreSQL target.
2. Restore the selected backup.
3. Verify table count and migration history.
4. Run:

    alembic current
    alembic heads

5. Run the application migration only if the restored database is intentionally being brought forward.
6. Verify critical tables: organizations, users, episodes, assets, processing_jobs, subtitles, export_records.
7. Verify storage object references still point to the expected providers and keys.
8. Restart the API against the restored database.
9. Check /api/v1/health and application logs.
10. Only then allow normal writes.

## Post-restore checks

- Authentication works.
- Tenant scoping still applies.
- Latest episode data is present.
- Processing jobs are not accidentally marked completed.
- Export records are consistent.
- No secret values were written into database fields or logs.

A restore drill should be performed separately and recorded before claiming disaster-recovery readiness.
