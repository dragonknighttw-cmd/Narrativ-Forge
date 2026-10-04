# Managed PostgreSQL and Redis

This guide covers provisioning the managed data services used by the Narrativ
Forge API and worker. Provider-specific values such as service names, hostnames,
and connection URLs are supplied by the selected provider; replace the
placeholders below with those values. Do not commit connection strings or
credentials to Git.

## Managed PostgreSQL

Use a managed PostgreSQL service suitable for production: persistent storage,
TLS-protected connections, private networking where available, automated
backups with point-in-time recovery, and enough storage, connection capacity,
and compute for the expected workload. PostgreSQL 16 matches the integration
service currently used in CI; select a provider-supported PostgreSQL version
compatible with the application.

1. Create a managed PostgreSQL instance and database in the deployment region.
   Enable provider-required network access and TLS settings.
2. Create an application database user with only the permissions needed by the
   application and its Alembic migrations.
3. Obtain the provider's connection URL and configure it as `DATABASE_URL` in
   the deployment platform's protected environment settings. Use the provider's
   TLS connection option when required. URL-encode reserved characters in
   usernames or passwords; do not put the URL in source files, logs, or
   committed environment files.
4. The application supports PostgreSQL through its existing database
   configuration and `psycopg2` driver (`psycopg2-binary` in
   `web-platform/backend/requirements.txt`). Its existing URL normalization
   converts `postgres://` and `postgresql://` URLs to the
   `postgresql+psycopg2` SQLAlchemy driver. Preserve the provider URL's
   credentials and parameters; no application URL rewrite is required.
5. From `web-platform/backend`, with `DATABASE_URL` available in the protected
   environment, apply migrations:

   ```sh
   python -m alembic upgrade head
   python -m alembic current
   ```

   Production and staging use Alembic rather than automatic table creation.
   The API `startCommand` in the current `render.yaml` also runs
   `alembic upgrade head` before starting Uvicorn.
6. Verify a database connection from `web-platform/backend` in an environment
   with the same `DATABASE_URL`:

   ```sh
   python -c "from sqlalchemy import text; from app.db import engine; connection = engine.connect(); print(connection.execute(text('SELECT 1')).scalar_one()); connection.close()"
   ```

   A successful check prints `1`. Do not print or expose the connection URL.

## Managed Redis

Redis is required by the Phase 1/Phase 2 infrastructure direction, even though
the current application configuration permits it to be absent during local
development. CI currently uses Redis 7; use a provider-supported Redis or
Redis-compatible managed service with adequate capacity and access controls.

1. Create a managed Redis instance/service in the deployment region and
   restrict network access to the application where the provider allows it.
2. Obtain its Redis connection URL from the provider. Configure it as
   `REDIS_URL` in protected environment settings; never commit the URL or its
   credentials. If the provider supplies a TLS endpoint, use that secure URL
   (commonly `rediss://`) and follow the provider's certificate and TLS
   requirements. Do not downgrade to an unencrypted endpoint to work around a
   connection failure.
3. Verify connectivity from `web-platform/backend` in an environment with the
   configured `REDIS_URL`:

   ```sh
   python -c "from app.infrastructure.redis import create_redis_client; client = create_redis_client(); print(client.ping()); client.close()"
   ```

   A successful check prints `True`. The client reads `REDIS_URL` from the
   application settings and connection failures are not suppressed.

## Configure the API and worker

The current deployment model uses the API and worker services declared in
[`../render.yaml`](../render.yaml). Configure protected environment variables
on **both** services:

| Variable | API service | Worker service |
| --- | --- | --- |
| `DATABASE_URL` | Managed PostgreSQL connection URL | The same managed PostgreSQL connection URL |
| `REDIS_URL` | Managed Redis connection URL | The same managed Redis connection URL |

`render.yaml` already declares `DATABASE_URL` for both services as externally
configured (`sync: false`); enter the secret connection URL through the
deployment platform, not in the manifest. The current manifest does not declare
`REDIS_URL`, so add it to each service's protected environment settings in the
deployment platform. Do not add provider-generated values or credentials to
Git. Keep both services pointed at the same intended database and Redis
instance. Migrations must complete before application code relies on the
database; the API start command in the manifest applies them before Uvicorn
starts.

## Deployment verification checklist

- [ ] Managed PostgreSQL is reachable from the deployment environment.
- [ ] Managed Redis is reachable from the deployment environment using the
      provider's required TLS settings.
- [ ] Alembic migrations have been applied and `alembic current` reports the
      expected head.
- [ ] The API starts successfully and its `/api/v1/health` endpoint responds.
- [ ] The worker starts successfully with the same `DATABASE_URL` and
      `REDIS_URL`.
- [ ] No connection strings, passwords, or other secrets have been committed.
- [ ] CI remains green, including PostgreSQL and Redis integration tests.
