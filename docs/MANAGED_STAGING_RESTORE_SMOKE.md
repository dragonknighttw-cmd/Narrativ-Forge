# Managed destination restore smoke test

## Current scope

The manual workflow `.github/workflows/managed-staging-restore-evidence.yml` uses an ephemeral PostgreSQL 17 service as its source and the approved Supabase project `Narrativ-Forge-1` (`oeqyheycywqkgeeqmpxa`) as its destination.

It does not use the primary `Narrativ-Forge` database as a source or target. It tests PostgreSQL backup/restore mechanics using a minimal fixture; it does not restore or verify the full Narrativ-Forge application schema.

## GitHub Environment configuration

In repository Settings → Environments → `managed-staging-restore`, configure:

- Secret: `STAGING_RESTORE_DATABASE_URL` — PostgreSQL connection URL for `Narrativ-Forge-1`; keep the value private.

The workflow checks the URL hostname directly against the approved destination host (`db.oeqyheycywqkgeeqmpxa.supabase.co`), so no separate host variable is required. It rejects a URL whose hostname differs from that approved host. Before restore, it refuses unexpected public base tables; the only tables permitted for a repeat smoke run are `alembic_version` and `organizations`.

## Run and evidence

Open Actions → Managed Staging Restore Evidence → Run workflow. Set `confirm_restore` to `true` only after verifying that the destination is `Narrativ-Forge-1`; leave it `false` to skip the job. Review the `managed-staging-restore-evidence` artifact and the workflow's exact commit SHA.

The evidence manifest marks `managed_destination_restore_smoke_verified` true only after success. It always leaves `application_schema_verified` and `production_verified` false. A successful smoke run is not proof of production recovery.

## Free-plan constraint

Supabase rejected creating another project because the organization reached its two-active-project Free-plan limit. No existing project was deleted or paused.
