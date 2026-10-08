# Database

> Owner: Backend/data maintainers  
> Update when: schema, migration, indexing, backup, or database-provider policy changes  
> Last Updated: 2026-10-08  
> Do NOT put here: connection strings

## Source of truth

PostgreSQL is the durable application/workflow database. The application connects through `DATABASE_URL`. Provider identity is not assumed from generic PostgreSQL configuration.

## Schema

SQLAlchemy models define application entities including organizations, users, episodes, assets, processing jobs, subtitles, export records, audit data, and production/analytics records.

## Migrations

Alembic is authoritative for schema changes. Forward migrations are preferred. Do not rely on automatic table creation in production.

The repository audit identifies migration revision `0017_asset_deleted_at` as the latest repository migration. The **live database head is VERIFY** until checked in the target environment.

Recommended checks:

```sh
python -m alembic upgrade head
python -m alembic current
python -m alembic heads
```

## Data rules

- Preserve approved output.
- Preserve original assets.
- Maintain tenant/resource authorization.
- Add indexes for important foreign-key/query paths.
- Do not expose service-role database access to the frontend.

## Backup/recovery

Backup and restore must be tested against a real managed PostgreSQL environment before production readiness is claimed. Restore must preserve workflow state, tenant isolation, and storage references.

## Live Alembic head verification

**Status: VERIFY — 2026-10-08.**

The live API is connected to PostgreSQL and Render logs show `alembic upgrade head` during startup. However, the connected Render account exposes **no Render-managed Postgres instance**, so the production `DATABASE_URL` is necessarily an external/provider-managed connection from the evidence available here.

Current tools cannot reveal the production secret value or directly query that external PostgreSQL instance. Therefore the exact live `alembic_version.version_num` remains unverified.

Owner verification command against the actual production database:

```sql
SELECT version_num FROM alembic_version;
```

Record the result and compare it with repository head `0017_asset_deleted_at`.
