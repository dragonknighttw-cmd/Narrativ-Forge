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
